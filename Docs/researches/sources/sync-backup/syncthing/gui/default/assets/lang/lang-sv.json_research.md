# sources/sync-backup/syncthing/gui/default/assets/lang/lang-sv.json

## Purpose
`lang-sv.json` is the Swedish translation catalog for the Syncthing default web GUI. It covers the full current English base catalog, including device/folder management, discovery and listener status, file versioning, ignore rules, authentication, sharing helpers, ownership and extended attributes, and connection transport labels.

## APIs, types, and data shape
The file is a flat JSON object consumed by Angular Translate. It has no functions or classes. The parsed catalog contains 558 keys, matching the 558-key English base exactly: no missing keys, no extra keys, no empty values, and no placeholder-token mismatches. Ten values are intentionally or plausibly identical to English, including acronyms and protocol labels such as `LDAP`, `QUIC LAN`, `TCP WAN`, `OK`, and `Version`.

## Control flow
When `LocaleService` selects Swedish, `$translate.use('sv')` activates this lookup table. Template `translate` attributes, translate filters, and controller calls resolve through this map, including dynamic strings using translated values with `{{...}}` interpolation placeholders.

## State and persistence behavior
The catalog is static. Runtime state is limited to the translation service cache and the user-selected locale persisted separately through `SYN_LANG` in localStorage. This file does not affect Syncthing configuration or synchronization state.

## Dependencies and integration points
The file integrates with `valid-langs.js`, which includes `sv`, and with the global display-name table from `prettyprint.js` used by the language selector. It depends on Angular Translate and the generated Weblate catalog pipeline documented by the asset directory README.

## Risks
Structural risk is low because coverage and placeholders match the English base. Remaining risks are linguistic quality, strings that intentionally stay English, and generated-file drift if the English catalog changes without a corresponding Weblate update. Long Swedish text can still stress modal, table, or button layouts.

## Test signals
Run JSON parse, exact key-set equality with `lang-en.json`, placeholder parity, and UI smoke tests after selecting Swedish. Useful paths include settings, add/edit device, add/edit folder, receive-encrypted folder warnings, sharing by email/SMS, logs, and version restore dialogs.
