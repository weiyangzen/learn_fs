# sources/sync-backup/syncthing/gui/default/assets/lang/lang-nl.json

## Purpose

`lang-nl.json` supplies Dutch translations for the Syncthing default web GUI. It is a generated Weblate asset under `gui/default/assets/lang`; the adjacent `README.txt` says the files are auto-generated and should be updated through Weblate rather than by hand.

The file is a JSON object with 551 top-level entries. Compared with `lang-en.json`'s 558 entries, it is missing 7 English source keys: `Block Indexing`, `Device Group`, `Folder Group`, `Maintain an index of all blocks in the folder...`, `Optional group for the device...`, `Optional group for the folder...`, and `Starting`. It has no extra keys versus English and no empty string values.

## Important APIs, Types, and Data Shape

There are no executable functions or classes. The exported API is the static JSON translation table fetched by angular-translate's static file loader. Most entries are `string -> string` phrase mappings, for example UI labels, warning text, modal copy, tooltip text, status strings, and file operation terms.

One top-level value is an object: `theme.name` maps theme IDs such as `black`, `dark`, `default`, and `light` to Dutch display names. This nested object is important because `syncthing/core/syncthingController.js` calls `$translate.instant("theme.name." + theme)` in `themeName()`.

Interpolation placeholders follow the project convention where source keys contain markers like `{%name%}` and translated values use Angular interpolation such as `{{name}}`. That is expected by angular-translate and `$interpolate`; it should not be treated as a mismatch by tests.

## Control Flow and Runtime Use

`syncthing/app.js` configures `$translateProvider.useStaticFilesLoader({ prefix: 'assets/lang/lang-', suffix: '.json' })` and sets fallback language `en`. When Dutch is selected, angular-translate loads `assets/lang/lang-nl.json`, merges it into the translation table for locale `nl`, and uses entries from this file to resolve `translate` directives and `translate` filters in `index.html` and modal templates.

Locale selection is mediated by `LocaleService` in `syncthing/core/localeService.js`. The service receives available locales from `validLangs`, reads the browser's accepted language list from `/rest/svc/lang`, honors a `?lang=` query parameter, and calls `$translate.use(language)`. Because `valid-langs.js` includes `nl`, Dutch appears in the language selector and can be selected by users.

When a Dutch key is absent, angular-translate falls back to English because `fallbackLanguage('en')` is configured. For the 7 missing Dutch entries, the GUI will therefore show English text rather than fail.

## State and Persistence Behavior

This file has no mutable state. Its runtime effect becomes part of angular-translate's in-memory translation table after the static JSON request succeeds.

User language preference is persisted outside this file by `LocaleService` under the `localStorage` key `SYN_LANG` when selection is made through the UI or `?lang=`. The document `<html lang>` attribute is updated to the active language after `$translate.use(...)` succeeds.

## Dependencies and Integration Points

Primary dependencies are `pascalprecht.translate`, `angular-translate-loader-static-files`, Angular `$interpolate`, and the global `validLangs` / `langPrettyprint` assets. The source phrases are referenced across `index.html` and templates in `syncthing/{core,device,folder,settings,transfer,usagereport}`.

The file is integrated by name: locale code `nl` maps directly to `lang-nl.json`. It also participates in theme display via `theme.name.*`.

## Risks

The main functional risk is drift from `lang-en.json`: missing keys silently fall back to English, which can produce mixed-language UI. The currently observed missing keys are around block indexing and device/folder grouping, so those newer settings may be less localized.

Thirteen string entries have values identical to their keys. Many are abbreviations or technical terms (`GUI`, `LDAP`, `QUIC LAN`, `TCP WAN`), but entries such as `Help`, `Info`, `Type`, and `items` should be checked by Dutch reviewers because exact equality may indicate intentionally borrowed words or untranslated leftovers.

Because this is generated content, manual edits are at risk of being overwritten by Weblate synchronization.

## Test Signals

Useful checks are: `jq` parses the file; all top-level values are strings except the expected `theme` object; no value is empty; keys stay a subset of `lang-en.json` unless the translation system intentionally adds locale-only aliases; placeholder variables in translated values remain compatible with the source phrase; and `valid-langs.js` continues to include `nl`.

Runtime smoke coverage should open the GUI with `?lang=nl`, verify that the language selector lists Dutch, confirm `SYN_LANG=nl` is persisted after selection, and inspect settings screens for English fallback around the 7 missing keys.
