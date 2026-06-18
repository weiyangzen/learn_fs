# sources/sync-backup/syncthing/gui/default/assets/lang/lang-bg.json

## Purpose
This JSON file provides Bulgarian translations for the Syncthing web GUI. It is a full enabled language asset mapping English GUI strings to Bulgarian strings.

## Important APIs, Types, And Functions
The file contains 558 top-level keys, no empty string values, and one object-valued `theme` key containing Bulgarian theme names for black, dark, default, and light. It is consumed by `angular-translate` via the static language file loader. Bulgarian `bg` is present in `valid-langs.js` and `prettyprint.js`, so it is available through normal language selection.

## Control Flow
When the selected locale is `bg`, the GUI requests `assets/lang/lang-bg.json`. Translation directives and filters look up English source keys in this object, interpolate values through Angular syntax such as `{{foldertype}}`, and fall back to English for any missing key.

## State And Persistence Behavior
The file is generated translation data and stores no runtime state. It is loaded by the browser as a static asset and cached according to normal web asset behavior.

## Dependencies And Integration Points
It integrates with Angular templates, source string extraction, language metadata files, and Weblate automation. The nested `theme.name` object is an integration point for theme display labels rather than ordinary sentence translation. Placeholder-heavy strings must preserve variable names from templates.

## Risks And Edge Cases
Bulgarian text length can differ significantly from English and may stress compact UI elements. Placeholder or quote mismatches can break interpolation or produce awkward modal text. Because this is generated, manual edits are fragile. Full key count matching does not guarantee quality; some translated strings may still contain terminology or grammar issues.

## Test Signals
`jq` validates the file and shows 558 keys. GUI testing should switch to Bulgarian, inspect common settings/device/folder dialogs, verify placeholder substitutions, and check theme labels. Automated checks should compare key and placeholder parity with the English catalog.
