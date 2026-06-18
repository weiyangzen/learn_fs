# sources/sync-backup/syncthing/gui/default/assets/lang/prettyprint.js

## Purpose
This file defines the global `langPrettyprint` map used by the Syncthing GUI language selector to display human-readable language names for available locale codes.

## Important APIs, types, and functions
The only exported surface is a global variable assignment: `var langPrettyprint = { ... }`. Keys are locale identifiers such as `en`, `pt-BR`, `zh-CN`, `zh-HK`, and `zh-TW`; values are English display names. It is not an ES module or Angular service, so consumers access it as a browser global.

## Control flow and integration
There is no control flow. `LocaleService.getLocalesDisplayNames()` returns this global map, and `languageSelectDirective.js` filters it against `LocaleService.getAvailableLocales()`. The language selector inverts names to codes, sorts by display name, and shows bracketed codes for available locales missing from this map.

## State and persistence behavior
The file is stateless. It affects presentation only; language selection persistence is handled by `LocaleService`.

## Dependencies and integration points
It must be loaded before `LocaleService.getLocalesDisplayNames()` is called. It should stay consistent with `valid-langs.js` and the actual `lang-*.json` assets. Locale codes need exact spelling because they also drive static JSON filenames.

## Risks
Mismatches between `langPrettyprint`, `validLangs`, and catalog files can cause missing selector labels or unselectable translations. Duplicate display names are risky because `languageSelectDirective.js` inverts the map by display name, so later entries with the same name can overwrite earlier locale codes. Because names are sorted as strings, display-name changes affect selector order.

## Test signals
Check that every code in `valid-langs.js` has a corresponding pretty name and a `lang-<code>.json` file, and that no duplicate display names collapse when inverted. Browser smoke testing should confirm the dropdown labels for `zh-CN`, `zh-HK`, and `zh-TW`.
