# sources/sync-backup/syncthing/gui/default/assets/lang/lang-he-IL.json

## Purpose

`lang-he-IL.json` is the Hebrew (Israel) runtime translation catalog for the Syncthing AngularJS web GUI. It is loaded as `assets/lang/lang-he-IL.json` when the active locale is `he-IL`, translating English message IDs used across the GUI.

The file is generated from Weblate, and `he-IL` is listed in `valid-langs.js` and `prettyprint.js` as `Hebrew (Israel)`, making it available in the GUI language selector.

## Important APIs, Types, and Data Shape

The file is a JSON object with 551 top-level keys. It has 550 string values and one nested `theme.name` object for theme labels. English strings are lookup IDs; translated Hebrew strings are values; nested theme IDs are represented as objects.

The catalog is consumed through Angular Translate's static file loader. Interpolation placeholders are part of the data contract and must match the source ID variables.

## Control Flow, State, and Persistence

Locale selection flows through `LocaleService`: URL parameter, persisted `SYN_LANG`, or browser language data from `/rest/svc/lang`. Calling `$translate.use('he-IL')` loads this file; translated strings are then applied by template `translate` attributes, translate filters, and JavaScript `$translate.instant(...)` calls.

The JSON file is static data. Persistent user language choice is external and stored as `SYN_LANG` in localStorage when explicitly selected. Successful use of this locale sets the HTML `lang` attribute to `he-IL`.

## Dependencies and Integration Points

Runtime dependencies are AngularJS, Angular Translate, the static file loader, `LocaleService`, `valid-langs.js`, `prettyprint.js`, and GUI static asset serving. Maintenance dependencies are Weblate, the Weblate token used by the download script, JSON validity, and the English source catalog used as the key baseline.

## Risks and Test Signals

Compared with `lang-en.json`, Hebrew is missing 7 top-level keys and has no extras. Missing entries include `Block Indexing`, `Device Group`, `Folder Group`, the block-indexing help text, optional group help text, and `Starting`; those strings fall back to English.

Placeholder parity checks found no mismatched placeholder names. The largest locale-specific risk is RTL rendering: this file contains Hebrew strings but does not encode directionality, and the Angular loader only sets `document.documentElement.lang`. Validation signals: `jq -e .` succeeds; size is 55,245 bytes and 560 lines; key count is 551; value distribution is 550 strings and one object; `he-IL` is registered in `valid-langs.js` and `prettyprint.js`.
