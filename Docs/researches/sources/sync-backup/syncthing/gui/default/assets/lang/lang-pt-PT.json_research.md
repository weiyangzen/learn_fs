# sources/sync-backup/syncthing/gui/default/assets/lang/lang-pt-PT.json

## Purpose

`lang-pt-PT.json` supplies European Portuguese translations for the Syncthing default web GUI. It is a generated Weblate translation asset loaded by the AngularJS frontend.

The file is a JSON object with 548 top-level entries. Compared with `lang-en.json`'s 558 entries, it is missing 10 keys: `Block Indexing`, `Debug`, `Device Group`, `Folder Group`, `Info`, `Limit Bandwidth in LAN`, `Maintain an index of all blocks in the folder...`, `Optional group for the device...`, `Optional group for the folder...`, and `Starting`. It has no extra keys and no empty string values.

## Important APIs, Types, and Data Shape

This file contains static localization data rather than functions. It exports 547 string mappings plus a nested `theme.name` object. Top-level string keys are English source phrases used by templates and controllers; values are European Portuguese translations.

Translated values use Angular interpolation markers such as `{{name}}`, `{{count}}`, and `{{receiveEncrypted}}` for runtime values. The source keys often use the Syncthing translation placeholder notation `{%...%}`; angular-translate resolves the translated value through Angular `$interpolate`.

The nested `theme.name` object is consumed by `themeName()` for the GUI theme selector.

## Control Flow and Runtime Use

When the active locale is `pt-PT`, `$translate.use('pt-PT')` loads `assets/lang/lang-pt-PT.json` through the static file loader configured in `syncthing/app.js`. The loaded table backs `translate` directives, filters, tooltip translations, and controller calls.

`valid-langs.js` includes `pt-PT`, so European Portuguese is available in the language dropdown and participates in browser-language matching through `LocaleService`.

The globally configured fallback is English. The 10 missing keys will display in English rather than causing errors, with likely visibility in newer settings around block indexing, grouping, LAN bandwidth limiting, and debug/status labels.

## State and Persistence Behavior

The file has no own state and no persistence. angular-translate stores the loaded locale table in memory.

`LocaleService` handles persistence externally: selecting this locale can store `SYN_LANG=pt-PT` in `localStorage`, and the HTML document language is set to `pt-PT` after activation.

## Dependencies and Integration Points

Dependencies are angular-translate, the static file loader, Angular interpolation/sanitization, `valid-langs.js`, and locale display data from `prettyprint.js`. The file integrates with all GUI templates/controllers that use English source phrases as translation IDs.

The `theme.name.*` entries integrate specifically with the settings view's theme selector through `syncthingController.js`.

## Risks

The main risk is partial catalog drift. Missing keys are few but user-visible, and fallback to English can create mixed-language settings and status screens. The missing `Debug` and `Info` labels are short but visible; missing block-indexing and grouping descriptions may affect comprehension of advanced folder/device settings.

Six values are identical to their keys: `LDAP`, `OK`, `QUIC LAN`, `QUIC WAN`, `TCP LAN`, and `TCP WAN`. These are likely intentional technical labels.

Because this file is generated, direct edits are fragile and should be made upstream in Weblate.

## Test Signals

Static checks should parse the JSON, compare the key set with English, report the 10 missing keys, assert no extra keys and no empty values, and verify that `theme.name` is present.

Runtime smoke tests should open `?lang=pt-PT`, ensure the language selector lists European Portuguese, verify `SYN_LANG=pt-PT` persistence, exercise settings areas tied to the missing keys to confirm English fallback is acceptable, and inspect interpolated confirmation dialogs for correct dynamic values.
