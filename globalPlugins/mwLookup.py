# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys

import webbrowser
from pathlib import Path

import addonHandler
import wx
addonHandler.initTranslation()

from logHandler import log
import globalPluginHandler
from scriptHandler import script
import ui
import api
import winUser
import gui

# Global gesture to open the dialog (always available).
OPEN_GESTURE = "kb:control+alt+shift+d"
MAX_SELECTION_CHARS = 60


def _getSelectedText(maxChars: int = 60) -> str:
    """Return currently selected text (prefer virtual buffers), trimmed and normalized.

    Notes:
    - In normal edit controls (Notepad/Word/etc.), selection usually lives on the focused NVDAObject.
    - In browsers (Chrome/Firefox) while in Browse Mode, selection is tracked on the TreeInterceptor
      (virtual buffer), not necessarily on the focused object.
    """

    def _normalize(s: str) -> str:
        # Collapse all whitespace (including newlines) into single spaces.
        return " ".join((s or "").split()).strip()

    try:
        focus = api.getFocusObject()
        if not focus:
            return ""

        # Prefer virtual buffer selection when available (Chrome/Firefox Browse Mode).
        candidates = []
        ti = getattr(focus, "treeInterceptor", None)
        if ti:
            candidates.append(ti)
        candidates.append(focus)

        # 1) Try explicit selection.
        for obj in candidates:
            try:
                txtInfo = obj.makeTextInfo("selection")
                txt = _normalize(getattr(txtInfo, "text", "") or "")
                if txt:
                    return txt[:maxChars]
            except Exception:
                continue

        # 2) Fallback: word at caret (helps when nothing is selected).
        for obj in candidates:
            try:
                txtInfo = obj.makeTextInfo("caret")
                try:
                    txtInfo.expand("word")
                except Exception:
                    # Some text providers may not support expand; ignore.
                    pass
                txt = _normalize(getattr(txtInfo, "text", "") or "")
                if txt:
                    return txt[:maxChars]
            except Exception:
                continue

        return ""
    except Exception:
        return ""


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    """
    Merriam-Webster Lookup GlobalPlugin.

    - Keeps ONE global gesture to open the dialog.
    - Dynamically binds dialog-only gestures *only while focus is inside the lookup dialog*,
      so they show up in Input Help (NVDA+1) and do not interfere elsewhere.
    """

    scriptCategory = _("Merriam-Webster Lookup")

    __gestures = {
        OPEN_GESTURE: "openLookupDialog",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dlg = None
        self._localGesturesBound = False
        self._headingGesturesBound = False
        

    def _ensureDialog(self):
        """Create (or return) the wx dialog, focusing it if already open."""
        try:
            if self._dlg and getattr(self._dlg, "IsShown", lambda: False)():
                try:
                    # Best-effort focus.
                    import wx  # type: ignore
                    wx.CallAfter(self._dlg.Raise)
                    wx.CallAfter(self._dlg.SetFocus)
                except Exception:
                    pass
                return self._dlg

            # Late import so plugin load stays robust.
            try:
                from mwLookupLib.dialog import LookupDialog  # type: ignore
            except Exception:
                # Fallback path inside add-on.
                baseDir = os.path.dirname(os.path.dirname(__file__))
                libDir = os.path.join(baseDir, "lib")
                if libDir not in sys.path:
                    sys.path.insert(0, libDir)
                from mwLookupLib.dialog import LookupDialog  # type: ignore

            import wx  # type: ignore
            self._dlg = LookupDialog(gui.mainFrame)  # type: ignore[name-defined]
            wx.CallAfter(self._dlg.Show)
            wx.CallAfter(self._dlg.Raise)
            wx.CallAfter(self._dlg.SetFocus)
            return self._dlg
        except Exception:
            log.exception("mwLookup: failed to create dialog")
            self._dlg = None
            ui.message(_("Failed to open the Merriam-Webster Lookup dialog. Check NVDA Log Viewer."))
            return None

    def _focusHwnd(self) -> int:
        try:
            obj = api.getFocusObject()
            return int(getattr(obj, "windowHandle", 0) or 0)
        except Exception:
            return 0

    def _dlgHwnd(self) -> int:
        try:
            if not self._dlg:
                return 0
            return int(self._dlg.GetHandle())
        except Exception:
            return 0

    def _moreExamplesHwnd(self) -> int:
        """Return the HWND for the Example Sentences dialog, if open."""
        try:
            if not self._dlg:
                return 0
            ex = getattr(self._dlg, "_moreExamplesDlg", None)
            if not ex:
                return 0
            return int(ex.GetHandle())
        except Exception:
            return 0

    def _moreExamplesTextHwnd(self) -> int:
        """Return the HWND for the Example Sentences dialog text control, if open."""
        try:
            if not self._dlg:
                return 0
            ex = getattr(self._dlg, "_moreExamplesDlg", None)
            if not ex:
                return 0
            tc = getattr(ex, "_textCtrl", None)
            if not tc:
                return 0
            return int(tc.GetHandle())
        except Exception:
            return 0

    def _focusInsideMoreExamplesDialog(self) -> bool:
        """Return True if focus is inside the Example Sentences (View more examples) dialog."""
        moreHwnd = self._moreExamplesHwnd()
        if not moreHwnd:
            return False
        focusHwnd = self._focusHwnd()
        if not focusHwnd:
            return False
        try:
            return bool(winUser.isDescendantWindow(moreHwnd, focusHwnd)) or (moreHwnd == focusHwnd)
        except Exception:
            return False

    def _isMoreExamplesOpen(self) -> bool:
        """Return True if the Example Sentences dialog is currently open and shown."""
        try:
            if not self._dlg:
                return False
            ex = getattr(self._dlg, "_moreExamplesDlg", None)
            if not ex:
                return False
            return bool(getattr(ex, "IsShown", lambda: False)())
        except Exception:
            return False

    def _focusInsideDialog(self) -> bool:
        dlgHwnd = self._dlgHwnd()
        moreHwnd = self._moreExamplesHwnd()
        focusHwnd = self._focusHwnd()
        if not focusHwnd:
            return False
        try:
            if dlgHwnd and (bool(winUser.isDescendantWindow(dlgHwnd, focusHwnd)) or (dlgHwnd == focusHwnd)):
                return True
            if moreHwnd and (bool(winUser.isDescendantWindow(moreHwnd, focusHwnd)) or (moreHwnd == focusHwnd)):
                return True
            return False
        except Exception:
            return False

    

    def _resultsHwnd(self) -> int:
        try:
            if not self._dlg or not hasattr(self._dlg, "resultsCtrl"):
                return 0
            return int(self._dlg.resultsCtrl.GetHandle())
        except Exception:
            return 0

    def _focusInsideResults(self) -> bool:
        resHwnd = self._resultsHwnd()
        if not resHwnd:
            return False
        focusHwnd = self._focusHwnd()
        if not focusHwnd:
            return False
        try:
            return bool(winUser.isDescendantWindow(resHwnd, focusHwnd)) or (resHwnd == focusHwnd)
        except Exception:
            return False

    def _focusInsideMoreExamplesText(self) -> bool:
        """Return True if focus is inside the Example Sentences dialog text control."""
        tHwnd = self._moreExamplesTextHwnd()
        if not tHwnd:
            return False
        focusHwnd = self._focusHwnd()
        if not focusHwnd:
            return False
        try:
            return bool(winUser.isDescendantWindow(tHwnd, focusHwnd)) or (tHwnd == focusHwnd)
        except Exception:
            return False

    def _bindLocalGestures(self):
        if self._localGesturesBound:
            return
        try:
            self.bindGestures({
                "kb:alt+e": "focusSearch",
                "kb:alt+t": "focusResults",
                "kb:alt+r": "focusModeRadio",
                "kb:alt+s": "openSettings",
                "kb:alt+w": "openWordOfTheDay",
                "kb:alt+p": "openWordplay",
                "kb:alt+m": "openGrammarUsage",
                "kb:alt+c": "pressSearchButton",
                "kb:alt+d": "lookupSelection",
                "kb:alt+g": "lookupSelectionSlang",
                "kb:alt+a": "lookupSelectionThesaurus",
                "kb:alt+h": "focusHistory",
                "kb:alt+b": "browseWords",
                "kb:alt+f": "openFavorites",
                "kb:alt+l": "openSlangTrending",
                "kb:control+f": "find",
                "kb:f3": "findNext",
                "kb:shift+f3": "findPrev",
                "kb:f1": "openHelpInBrowser",
                "kb:f7": "chooseHeading",
                "kb:a": "nextAudio",
                "kb:shift+a": "prevAudio",
                "kb:h": "nextHeading",
                "kb:shift+h": "prevHeading",
                "kb:l": "nextList",
                "kb:shift+l": "prevList",            })
            self._localGesturesBound = True
        except Exception:
            # Never let gesture binding break plugin loading.
            log.exception("mwLookup: failed to bind local gestures")
            self._localGesturesBound = False

    def _unbindLocalGestures(self):
        if not self._localGesturesBound:
            return
        try:
            # IMPORTANT:
            # NVDA's clearGestureBindings() clears *all* gesture bindings for this plugin,
            # including the global "open dialog" gesture declared in __gestures.
            # If we clear without restoring it, the add-on will only open once per NVDA
            # session (until NVDA restarts).
            self.clearGestureBindings()
            # Restore the always-available global opener.
            self.bindGestures({OPEN_GESTURE: "openLookupDialog"})
        except Exception:
            log.exception("mwLookup: failed to unbind local gestures")
        self._localGesturesBound = False

    def event_gainFocus(self, obj, nextHandler):
        # Keep normal NVDA focus processing.
        try:
            nextHandler()
        finally:
            # Dynamically bind/unbind dialog-only gestures for Input Help.
            try:
                inside = self._focusInsideDialog()
                if inside:
                    self._bindLocalGestures()
                else:
                    self._unbindLocalGestures()
            except Exception:
                log.exception("mwLookup: gainFocus handler failed")

    @script(description=_("Open the Merriam-Webster Lookup dialog"))
    def script_openLookupDialog(self, gesture):
        dlg = self._ensureDialog()
        if not dlg:
            return
        sel = _getSelectedText(MAX_SELECTION_CHARS)
        if sel:
            try:
                dlg.setQuery(sel)
            except Exception:
                pass

    # ---- Dialog-only scripts (bound dynamically while focus is inside the dialog) ----

    @script(description=_("Focus the search field"))
    def script_focusSearch(self, gesture):
        if not self._dlg:
            return
        # While the "View more examples" dialog is open, do not allow navigating
        # to other controls in the main dialog.
        if self._isMoreExamplesOpen():
            return
        try:
            self._dlg.focusSearch()
        except Exception:
            pass


    @script(description=_("Open the add-on help in the default web browser"))
    def script_openHelpInBrowser(self, gesture):
        # Open doc\en\readme.html from this add-on in the user's default browser.
        try:
            addon = addonHandler.getCodeAddon()
            helpPath = os.path.join(addon.path, "doc", "en", "readme.html")
            if not os.path.isfile(helpPath):
                ui.message(_("Help file not found."))
                return
            webbrowser.open(Path(helpPath).resolve().as_uri())
        except Exception:
            log.exception("mwLookup: failed to open help in browser")
            ui.message(_("Unable to open help."))


    @script(description=_("Move focus to the results area"))
    def script_focusResults(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            self._dlg.focusResults()
        except Exception:
            pass

    @script(description=_("Move focus to the mode radio buttons"))
    def script_focusModeRadio(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            self._dlg.focusModeRadio()
        except Exception:
            pass

    @script(description=_("Open Settings"))
    def script_openSettings(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            self._dlg.activateSettings()
        except Exception:
            pass

    @script(description=_("Open Word of the Day"))
    def script_openWordOfTheDay(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            self._dlg.activateWordOfTheDay()
        except Exception:
            pass

    @script(description=_("Open Wordplay"))
    def script_openWordplay(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            # Defer opening the Wordplay dialog so the script returns immediately.
            wx.CallAfter(self._dlg.onOpenWordplayHome, None)
        except Exception:
            log.exception("mwLookup: Alt+P failed to open Wordplay")

    @script(description=_("Open Grammar & Usage"))
    def script_openGrammarUsage(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            wx.CallAfter(self._dlg.onOpenGrammarHome, None)
        except Exception:
            pass


    @script(description=_("Open Favorites"))
    def script_openFavorites(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            self._dlg.activateFavorites()
        except Exception:
            pass


    @script(description=_("Open Slang & Trending"))
    def script_openSlangTrending(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            wx.CallAfter(self._dlg.onOpenSlangTrending, None)
        except Exception:
            log.exception("mwLookup: Alt+L failed to open Slang & Trending")


    @script(description=_("Press the Search button"))
    def script_pressSearchButton(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            self._dlg.activateSearch()
        except Exception:
            pass

    @script(description=_("Move focus to History"))
    def script_focusHistory(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            self._dlg.focusHistory()
        except Exception:
            pass

    @script(description=_("Open Browse words"))
    def script_browseWords(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            # Defer opening the Browse dialog so the script returns immediately.
            # This prevents NVDA watchdog freezes and speech dropouts while the modal dialog is created.
            wx.CallAfter(self._dlg.onBrowseNearby, None)
        except Exception:
            log.exception("mwLookup: Alt+B failed to open Browse dialog")

    @script(description=_("Look up the selected text from results in Dictionary"))
    def script_lookupSelection(self, gesture):
        if not self._dlg:
            return
        # These selection-lookup shortcuts are results-only.
        # In the "View more examples" dialog they must be silent.
        if self._isMoreExamplesOpen():
            return
        try:
            self._dlg._onLookupSelectionInResults()
        except Exception:
            pass

    @script(description=_("Look up the selected text from results in Thesaurus"))
    def script_lookupSelectionThesaurus(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            self._dlg._onLookupSelectionInResultsThesaurus()
        except Exception:
            pass

    @script(description=_("Find text in results"))
    def script_find(self, gesture):
        if not self._dlg:
            return
        try:
            self._dlg._mwScript_find(None)
        except Exception:
            pass

    @script(description=_("Look up the selected text from results in Slang"))
    def script_lookupSelectionSlang(self, gesture):
        if not self._dlg:
            return
        if self._isMoreExamplesOpen():
            return
        try:
            self._dlg._onLookupSelectionInResultsSlang()
        except Exception:
            pass


    @script(description=_("Find next match in results"))
    def script_findNext(self, gesture):
        if not self._dlg:
            return
        try:
            self._dlg._mwScript_findNext(None)
        except Exception:
            pass

    @script(description=_("Find previous match in results"))
    def script_findPrev(self, gesture):
        if not self._dlg:
            return
        try:
            self._dlg._mwScript_findPrev(None)
        except Exception:
            pass

    @script(description=_("Move to next heading in results"))
    def script_nextHeading(self, gesture):
        # In Input Help, NVDA will announce the description automatically.
        # In normal mode, act when focus is in Results or in the Example Sentences dialog.
        if not self._dlg or not self._focusInsideDialog():
            try:
                gesture.send()
            except Exception:
                pass
            return
        try:
            if self._focusInsideResults():
                self._dlg._mwScript_nextHeading(gesture)
                return
            if self._focusInsideMoreExamplesText():
                ex = getattr(self._dlg, "_moreExamplesDlg", None)
                if ex is not None and hasattr(ex, "_jumpToHeading"):
                    ex._jumpToHeading(prev=False)
                    return
        except Exception:
            pass
        try:
            gesture.send()
        except Exception:
            pass

    @script(description=_("Move to previous heading in results"))
    def script_prevHeading(self, gesture):
        # In Input Help, NVDA will announce the description automatically.
        # In normal mode, act when focus is in Results or in the Example Sentences dialog.
        if not self._dlg or not self._focusInsideDialog():
            try:
                gesture.send()
            except Exception:
                pass
            return
        try:
            if self._focusInsideResults():
                self._dlg._mwScript_prevHeading(gesture)
                return
            if self._focusInsideMoreExamplesText():
                ex = getattr(self._dlg, "_moreExamplesDlg", None)
                if ex is not None and hasattr(ex, "_jumpToHeading"):
                    ex._jumpToHeading(prev=True)
                    return
        except Exception:
            pass
        try:
            gesture.send()
        except Exception:
            pass


    @script(description=_("Move to next list in results"))
    def script_nextList(self, gesture):
        # In Input Help, NVDA will announce the description automatically.
        # In normal mode, act when focus is in Results or in the Example Sentences dialog.
        if not self._dlg or not self._focusInsideDialog():
            try:
                gesture.send()
            except Exception:
                pass
            return
        try:
            if self._focusInsideResults():
                self._dlg._mwScript_nextList(gesture)
                return
            if self._focusInsideMoreExamplesText():
                ex = getattr(self._dlg, "_moreExamplesDlg", None)
                if ex is not None and hasattr(ex, "_jumpToList"):
                    ex._jumpToList(prev=False)
                    return
        except Exception:
            pass
        try:
            gesture.send()
        except Exception:
            pass

    @script(description=_("Move to previous list in results"))
    def script_prevList(self, gesture):
        # In Input Help, NVDA will announce the description automatically.
        # In normal mode, act when focus is in Results or in the Example Sentences dialog.
        if not self._dlg or not self._focusInsideDialog():
            try:
                gesture.send()
            except Exception:
                pass
            return
        try:
            if self._focusInsideResults():
                self._dlg._mwScript_prevList(gesture)
                return
            if self._focusInsideMoreExamplesText():
                ex = getattr(self._dlg, "_moreExamplesDlg", None)
                if ex is not None and hasattr(ex, "_jumpToList"):
                    ex._jumpToList(prev=True)
                    return
        except Exception:
            pass
        try:
            gesture.send()
        except Exception:
            pass




    @script(description=_("Go to heading in results"))
    def script_chooseHeading(self, gesture):
        # In Input Help, NVDA will announce the description automatically.
        # In normal mode, only act when focus is inside the dialog; otherwise pass through.
        if not self._dlg or not self._focusInsideDialog() or not self._focusInsideResults():
            try:
                gesture.send()
            except Exception:
                pass
            return
        try:
            wx.CallAfter(self._dlg.showHeadingChooser)
        except Exception:
            pass

    @script(description=_("Move to next audio pronunciation in results"))
    def script_nextAudio(self, gesture):
        # Announced by NVDA Input Help automatically.
        if not self._dlg or not self._focusInsideDialog() or not self._focusInsideResults():
            try:
                gesture.send()
            except Exception:
                pass
            return
        # Only act in Results; otherwise pass through for typing.
        if not self._focusInsideResults():
            try:
                gesture.send()
            except Exception:
                pass
            return
        try:
            self._dlg._mwScript_nextAudioPronunciation(gesture)
        except Exception:
            pass

    @script(description=_("Move to previous audio pronunciation in results"))
    def script_prevAudio(self, gesture):
        # Announced by NVDA Input Help automatically.
        if not self._dlg or not self._focusInsideDialog() or not self._focusInsideResults():
            try:
                gesture.send()
            except Exception:
                pass
            return
        if not self._focusInsideResults():
            try:
                gesture.send()
            except Exception:
                pass
            return
        try:
            self._dlg._mwScript_prevAudioPronunciation(gesture)
        except Exception:
            pass
