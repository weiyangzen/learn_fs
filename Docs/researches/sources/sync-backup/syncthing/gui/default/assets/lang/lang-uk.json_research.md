# sources/sync-backup/syncthing/gui/default/assets/lang/lang-uk.json

## Purpose
`lang-uk.json` is the Ukrainian translation catalog for the Syncthing default web GUI. It is nearly complete and covers most device, folder, synchronization, configuration, discovery, authentication, notification, and status surfaces.

## APIs, types, and data shape
The file is a flat JSON object consumed as a translation table. It exposes no executable API. The parsed catalog contains 551 keys against the 558-key English base, about 98.7% coverage. There are no extra keys, no empty values, and no placeholder-token mismatches. Five protocol/acronym values remain identical to English: `LDAP`, `QUIC LAN`, `QUIC WAN`, `TCP LAN`, and `TCP WAN`.

## Control flow
When Ukrainian is selected, Angular Translate resolves English message IDs through this table. Strings are requested from templates through `translate` attributes and filters and from controllers through `$translate.instant(...)`. Missing entries fall through to global translation fallback behavior.

## State and persistence behavior
This catalog contains no mutable application state. Locale persistence is handled by `LocaleService` with the `SYN_LANG` localStorage key. The file has no direct relation to Syncthing configuration, folder state, or sync metadata persistence.

## Dependencies and integration points
`valid-langs.js` includes `uk`, so this locale is exposed through the language selector. The catalog depends on the English base keys, Angular Translate interpolation, display names from `prettyprint.js`, and the Weblate generation process noted in the directory README.

## Risks
The main risk is a small set of missing newer keys: `Block Indexing`, `Device Group`, `Folder Group`, the long block-indexing description, optional group descriptions for device and folder, and `Starting`. These gaps affect newer configuration/status UI and will fall back to English. Layout risk also exists for longer Ukrainian labels in narrow controls.

## Test signals
Validate JSON syntax, run key-set diff against `lang-en.json`, verify placeholder parity, and smoke-test Ukrainian through the visible language menu. Include screens for grouped devices/folders, block indexing, startup/status display, and common device/folder dialogs.
