# sources/sync-backup/syncthing/gui/default/assets/lang/lang-ca.json

## Purpose
This JSON file provides Catalan translations for the Syncthing web GUI. It maps English GUI source strings to Catalan strings and includes localized theme names.

## Important APIs, Types, And Functions
The file contains 551 top-level keys, no empty string values, and one nested `theme.name` object with Catalan names for black, dark, default, and light themes. It is loaded by Angular's static translation file loader as `assets/lang/lang-ca.json`. Catalan `ca` is present in `valid-langs.js` and has a display name in `prettyprint.js`.

## Control Flow
When the selected locale is `ca`, the GUI loads this JSON file, uses English strings from templates as lookup keys, interpolates Angular values such as `{{device}}`, `{{folder}}`, and `{{version}}`, and falls back to English for missing entries. Catalan also has a related `ca@valencia` file in the language directory, but this file covers the base `ca` locale.

## State And Persistence Behavior
The file is generated static translation data and stores no user state. Browser caching can retain old translations until assets refresh. The language directory README states that Weblate is the upstream source.

## Dependencies And Integration Points
It integrates with GUI templates, Angular translate, valid language metadata, pretty-printed language names, and theme selection UI. It must maintain exact source keys and interpolation variable names to stay compatible with templates.

## Risks And Edge Cases
The key count is slightly lower than Arabic/Bulgarian in this subset, so a few strings may fall back to English. Some strings include invisible or special punctuation around interpolations, which should be checked in rendered modals. Text expansion can affect buttons and table headings. Manual changes are likely overwritten by translation automation.

## Test Signals
`jq` validates the file and reports 551 keys. GUI checks should select Catalan, exercise settings/folder/device dialogs, verify interpolation-heavy prompts, and confirm fallback behavior for any missing strings. Automated checks should compare keys and placeholders against `lang-en.json`.
