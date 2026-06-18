# sources/sync-backup/syncthing/gui/default/assets/lang/lang-gl.json

## Purpose

`lang-gl.json` is the Galician runtime translation catalog for the Syncthing AngularJS web GUI. It provides translated values for English message IDs and is loaded as `assets/lang/lang-gl.json` when the current locale is `gl`.

The file is generated from Weblate, not intended for direct edits, and `gl` is registered in both `valid-langs.js` and `prettyprint.js` as `Galician`.

## Important APIs, Types, and Data Shape

The file is a JSON object with 550 top-level keys. It has 549 string values and one nested `theme.name` object. English strings are IDs; translated strings are values; nested theme IDs support dot-style lookup.

The catalog is consumed by Angular Translate's static file loader configured in `syncthing/app.js`. Interpolated IDs preserve the placeholder names used by templates and controllers.

## Control Flow, State, and Persistence

`LocaleService` selects `gl` from a URL override, stored language, or browser language negotiation. It calls `$translate.use('gl')`, which loads this file; GUI templates resolve `translate` directives and filters against the loaded map, with English fallback for missing IDs.

The catalog is static and stateless. User selection persistence is handled by `LocaleService` with localStorage key `SYN_LANG`; successful locale use updates the document `lang` attribute to `gl`.

## Dependencies and Integration Points

Runtime dependencies include AngularJS, Angular Translate, the static file loader, `/rest/svc/lang`, `valid-langs.js`, `prettyprint.js`, and the canonical English catalog for fallback. Maintenance dependencies are Weblate, `WEBLATE_TOKEN` for downloads, and the Go scripts under `script/`.

## Risks and Test Signals

Compared with `lang-en.json`, the Galician catalog is missing 8 top-level keys and has no extras. Missing entries include `Block Indexing`, `Device Group`, `Folder Group`, the deny-rules hint, block-indexing help text, optional group help text, and `Starting`; those IDs fall back to English.

Placeholder parity checks found no mismatched placeholder names. Validation signals: `jq -e .` succeeds; size is 49,513 bytes and 559 lines; key count is 550; value distribution is 549 strings and one object; `gl` is registered in `valid-langs.js` and `prettyprint.js`.
