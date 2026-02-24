---
lang: en
title: Merriam-Webster Lookup for NVDA
---

# Merriam-Webster Lookup for NVDA

**Author:** Amir Soleimani

## Introduction

Merriam-Webster Lookup for NVDA provides immediate, distraction-free
access to the full Merriam-Webster website experience directly within
NVDA. Dictionary, Thesaurus, and Slang content is presented in a clean,
structured format optimized specifically for screen reader users.
Non-essential and visually cluttered sections commonly found on the
website are removed to ensure a focused and efficient reading
experience.

This add-on intentionally uses the full Merriam-Webster website rather
than the limited API. The website provides richer editorial content,
more complete examples, dedicated Synonyms sections, structured word
history, and additional educational material that are not fully
available through the API. In addition, the Browse Words experience is
much more complete on the website than what is available through the
API. Wordplay and Grammar & Usage articles and categories are also
supported, and they are not available through the API.

The quickest way to open the add-on is the default gesture:
**Control+Alt+Shift+D**. You can invoke the add-on from anywhere to
instantly look up the word under the cursor or any currently selected
word or phrase. This allows seamless dictionary access while reading
documents, browsing the web, or working in any application.

From within the results, you can select any word or phrase and
immediately perform a new lookup in Dictionary, Thesaurus, or Slang.
This enables fast, interactive exploration without leaving the add-on.

Full audio pronunciation playback is supported directly inside NVDA
without opening a web browser. When multiple pronunciations are
available, you can navigate between them and play them instantly.

If no exact match is found, the add-on provides a list of suggestions to
help you quickly find the correct spelling or a related entry.

The add-on uses caching to speed up repeat lookups and reduce
unnecessary network requests. You can control caching and other options
in Settings.

## Requirements

-   **Minimum required NVDA version:** 2026.1
-   **Tested and compatible with:** NVDA 2026.1 through 2026.4
-   An active internet connection is required for lookups.

All keyboard shortcuts can be customized via:\
NVDA menu → Preferences → Input gestures → Merriam-Webster Lookup

## Quick Start

1.  Press **Control+Alt+Shift+D** to open the add-on.
2.  The word under the cursor or selected text will be used
    automatically (you can also type your own query). You can also press
    **Down Arrow** in the search combo box to access your previously
    searched items.
3.  If you type a word manually or select a previous search using **Down
    Arrow**, press **Enter** to immediately search using the default
    lookup mode (Dictionary) for faster access.
4.  Choose the desired mode using the available radio buttons
    (Dictionary or Thesaurus). Slang lookups can be performed directly
    from the Results area, or by using the Slang & Trending option.
5.  Press Search to retrieve results.
6.  If no exact match is found, review the Suggestions list and choose
    the best match.
7.  Use navigation commands (headings, lists, audio) to explore the
    content.
8.  Optional: Use the context menu for actions such as copying or
    looking up the selected text.

## Available Sources

### Dictionary

Provides full definitions, pronunciations, examples, word history,
derived forms, and related sections as available on Merriam-Webster.

### Thesaurus

Displays synonyms, antonyms, and related word groups with structured
navigation.

### Slang

Slang is not an independent source (there is no Slang radio button), and
it cannot be searched directly from the main Search controls. This
matches the Merriam-Webster website, which does not provide a standalone
Slang search mode. You can access Slang entries via the Results area,
via Browse Words, and via the Slang & Trending option.

## Results Area

The Results area behaves like a standard read-only text area: normal
text selection and standard reading/navigation commands work as
expected.

Entries include both textual pronunciations (IPA) and audio
pronunciations when available. Textual pronunciations appear directly
within the entry, and audio pronunciations can be navigated and played.

Important: if you select a word or phrase in Results, you can look it up
immediately using: **Alt+D** (Dictionary), **Alt+A** (Thesaurus), and
**Alt+G** (Slang).

## Navigating Results

-   H / Shift+H: Move between headings
-   L / Shift+L: Move between lists
-   A / Shift+A: Move between audio pronunciations
-   F7: Show a list of headings (Heading chooser)
-   Enter: Activate the current item

## History

The History list keeps track of recent lookups for quick revisiting.

-   **Dictionary and Thesaurus** maintain separate history lists.
-   **Slang** lookups are stored in the **Dictionary** history list,
    with the word **\"Slang\"** appended to the end of the item label.

History also provides a context menu for actions such as removing items.

## Browse Words

Browse Words lets you explore Merriam-Webster entries without typing a
specific query. It is context-sensitive:

-   **General browsing:** Choose a bucket such as A--Z, 0--9, BIO, or
    GEO to browse entries.
-   **Nearby words browsing:** When you open Browse Words from an active
    lookup, you can browse words related to the current entry (nearby
    words).

Browse lists include a context menu for actions such as looking up the
selected item, copying, or other list-specific actions.

## Word of the Day

Word of the Day opens a complete daily entry (including definitions,
examples, and related sections when available). This is a quick way to
discover new vocabulary using the same optimized reading experience.

At the beginning of the Word of the Day entry, options such as
**Previous** and **Next** are provided. When focused, press **Enter** to
move to earlier or later Word of the Day entries.

### Wordplay

Wordplay provides Merriam-Webster articles and topic-based categories.
Categories may contain multiple pages; when available, you can use the
Previous/Next page buttons to move between pages. Wordplay content is
not available through the API and is accessed directly from the website.

### Grammar & Usage

Grammar & Usage provides Merriam-Webster grammar and usage articles and
topic-based categories, similar to Wordplay. The Grammar & Usage home
page includes featured articles and a Popular section, followed by
categories such as Commonly Confused, Usage Notes, Spelling &
Pronunciation, and Punctuation. Category pages may contain multiple
pages; when available, use the Previous/Next page buttons to move
between pages. Grammar & Usage content is not available through the API
and is accessed directly from the website.

## Context Menus

Many parts of the add-on provide context menus to speed up common
actions. For example, list views such as Browse, Suggestions, History,
and Favorites include list-specific context menu items. The Results area
also provides a context menu with actions such as copying content or
performing a lookup on the selected text.

## View More Examples

View More Examples is available from the Results area context menu when
additional example sentences are provided by Merriam-Webster.

When opened, additional example sentences appear in a dedicated dialog.
While this dialog is open, other add-on windows and commands are
temporarily disabled to ensure a stable and focused reading experience.

Press Escape to close the View More Examples dialog.

## Favorites

Favorites allows you to save entries for quick future access. You can
add or remove items using the context menus available in: **Results**,
**History**, **Browse Words**, and the **Suggestions list**. Favorites
are stored separately for Dictionary and Thesaurus modes to keep your
saved entries organized.

Open Favorites using **Alt+F**. The Favorites list also provides a
context menu for managing saved entries, including removing individual
items.

## Settings

Settings lets you customize the add-on behavior. The Settings dialog is
organized into three tabs: **General**, **Cache**, and **Advanced**.

-   **General:** Includes main behavior options such as Default lookup
    mode, and History options (for example, history size or disabling
    history).
-   **Cache:** Control caching independently for text content and audio
    content. You can enable or disable each cache and clear cached items
    separately.
-   **Advanced:** Additional power-user options for fine-tuning the
    add-on behavior.

## Keyboard Shortcuts

### Global

| Shortcut | Action |
|---|---|
| Control+Alt+Shift+D | Open Merriam-Webster Lookup |
| F1 | Open this help file in the default web browser (press from inside the add-on) |


### Main Dialog

| Shortcut | Action |
|---|---|
| Alt+E | Focus the Search edit box |
| Alt+R | Focus source radio buttons |
| Alt+C | Activate Search |
| Alt+S | Open Settings |
| Alt+W | Open Word of the Day |
| Alt+F | Open Favorites |
| Alt+L | Open Slang & Trending |
| Alt+P | Open Wordplay |
| Alt+M | Open Grammar & Usage |
| Alt+B | Open Browse Words (context-sensitive) |
| Alt+H | Open History |


### Results Actions

| Shortcut | Action |
|---|---|
| Alt+D | Look up the selected word or phrase in Dictionary |
| Alt+A | Look up the selected word or phrase in Thesaurus |
| Alt+G | Look up the selected word or phrase in Slang |
| Alt+T | Move focus to the Results area |


### Results Navigation

| Shortcut | Action |
|---|---|
| H / Shift+H | Navigate between headings |
| L / Shift+L | Navigate between lists |
| A / Shift+A | Navigate between audio pronunciations |
| F7 | Heading chooser (list headings) |
| Enter | Activate the current item |


All shortcuts can be reassigned via NVDA Input Gestures:\
NVDA menu → Preferences → Input gestures → Merriam-Webster Lookup

## Notes

-   This add-on relies on the structure of the Merriam-Webster website.
-   An internet connection is required for lookups.
-   Content is provided by Merriam-Webster.
