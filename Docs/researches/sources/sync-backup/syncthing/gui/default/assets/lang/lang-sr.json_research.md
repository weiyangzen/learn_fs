# sources/sync-backup/syncthing/gui/default/assets/lang/lang-sr.json

## Purpose
`lang-sr.json` is the Serbian translation catalog for the Syncthing default web GUI. It currently covers only the beginning of the message catalog, mostly early alphabetic keys around device, address, add, network, and anonymous usage reporting copy.

## APIs, types, and data shape
This is a flat JSON object with English message IDs as keys and Serbian Cyrillic strings as values. It has no executable API. The parsed catalog contains 34 keys against 558 English keys, about 6.1% coverage. There are no extra keys, no empty values, no values left equal to English, and no placeholder mismatches for the single placeholder-bearing entry present.

## Control flow
Angular Translate uses the selected locale table as a lookup map. When a template contains `translate` or code calls `$translate.instant(...)`, the English message ID is looked up in this object. Missing Serbian entries are not handled here and will fall through according to the global translation configuration.

## State and persistence behavior
The file stores static localization data only. It has no state transitions and does not persist anything. User locale selection and persistence are handled by `LocaleService`, browser language detection through `/svc/lang`, and optional `SYN_LANG` storage.

## Dependencies and integration points
The catalog depends on the English key set, Angular Translate, and the Weblate-generated asset flow. `valid-langs.js` does not include `sr`, so this file is not currently advertised by the default language dropdown in the checked-in language list.

## Risks
The dominant risk is extremely low coverage: 524 base keys are missing, including common confirmation dialogs, settings, folder/device edit surfaces, status strings, and most newer features. Since it is not listed in `valid-langs.js`, there is also an integration risk where updates to this file do not affect the visible GUI without language-list regeneration.

## Test signals
Validate JSON syntax, diff keys against `lang-en.json`, check interpolation placeholder parity, and verify `sr` presence or absence in the generated available locale list. If the locale is enabled, test screens with both covered and uncovered strings to confirm fallback rendering.
