# sources/sync-backup/syncthing/gui/default/assets/lang/lang-fy.json

## Purpose

`lang-fy.json` is the Frisian runtime translation catalog for the Syncthing AngularJS web GUI. It supplies translations for English message IDs used in templates, filters, and JavaScript translation calls, and it is fetched as `assets/lang/lang-fy.json` when the active locale is `fy`.

The file is generated from Weblate according to the language directory README. `fy` is present in `valid-langs.js` and `prettyprint.js`, so it is offered in the GUI language dropdown as `Frisian`.

## Important APIs, Types, and Data Shape

The file is a JSON object with 441 top-level keys, all with string values. Unlike the current English baseline, it has no nested `theme` object, so theme names fall back to English or another fallback translation when Frisian is active.

The effective API is Angular Translate's static catalog contract: English UI strings are lookup IDs, translated strings are values, and interpolation variables must preserve source placeholder names. `syncthing/app.js` configures the loader with prefix `assets/lang/lang-` and suffix `.json`.

## Control Flow, State, and Persistence

When a user chooses Frisian or browser negotiation resolves to `fy`, `LocaleService.useLocale('fy')` calls `$translate.use('fy')`. Angular Translate loads this catalog and resolves UI message IDs against it, falling back to English for missing IDs.

The JSON catalog is immutable runtime data. Language state lives in browser localStorage key `SYN_LANG` when explicitly changed; a `?lang=fy` URL parameter overrides stored and browser-negotiated choices.

## Dependencies and Integration Points

Runtime dependencies are AngularJS, Angular Translate, the static files loader, `valid-langs.js`, `prettyprint.js`, and unauthenticated `/rest/svc/lang` negotiation. Generation integrates with `script/weblatedl.go`, `script/translate.go`, and Weblate.

## Risks and Test Signals

The main risk is coverage. Compared with `lang-en.json`, `lang-fy.json` is missing 117 top-level keys and has no extras. Missing entries include newer operational settings such as `Block Indexing`, `Device Group`, `Folder Group`, `Log In`, `Log Out`, `Listener Status`, `Maximum single entry size`, `Extended Attributes`, and `theme`. This produces mixed Frisian/English UI through fallback.

Placeholder parity checks found no mismatched placeholder names among existing string entries. Validation signals: `jq -e .` succeeds; size is 38,734 bytes and 443 lines; key count is 441; all values are strings; `fy` is registered in `valid-langs.js` and `prettyprint.js`.
