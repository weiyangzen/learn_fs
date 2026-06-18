# sources/sync-backup/syncthing/gui/default/assets/lang/lang-th.json

## Purpose
`lang-th.json` is the Thai translation catalog for the Syncthing default web GUI, but currently contains only one translated message: the duplicate-device-ID warning.

## APIs, types, and data shape
The file is a valid flat JSON object. It exports no executable API. The parsed catalog has 1 key against the 558-key English base, about 0.2% coverage. There are no extra keys, no empty values, and no placeholder mismatches.

## Control flow
If Thai were selected, Angular Translate would resolve only the one present message from this table. Every other translated template or controller string would be missing from this locale and would rely on the application translation fallback behavior.

## State and persistence behavior
This is static localization data. Locale choice and persistence are managed elsewhere by `LocaleService`, including browser-language detection and optional storage in `SYN_LANG`.

## Dependencies and integration points
The catalog depends on English message IDs and Angular Translate. `valid-langs.js` does not include `th`, so this file is not currently selectable through the default checked-in language menu. The directory README says language assets are generated from Weblate, so translation changes should flow through that service.

## Risks
The practical risk is that the file gives the appearance of Thai support while providing almost no UI coverage. If enabled, nearly all screens would fall back to English. Because only one string is present, there is little current interpolation risk, but future placeholder-bearing translations must preserve token names.

## Test signals
Validate JSON syntax, diff against `lang-en.json`, and confirm Thai is intentionally excluded from `valid-langs.js`. If enabling Thai, require much broader coverage and GUI smoke tests before exposing it in the language selector.
