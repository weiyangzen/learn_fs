# sources/sync-backup/syncthing/gui/default/assets/lang/lang-ga.json

## Purpose

`lang-ga.json` is the Irish runtime translation catalog for the Syncthing AngularJS web GUI. It is fetched as `assets/lang/lang-ga.json` when the selected or negotiated locale is `ga`, and it translates English message IDs used throughout GUI templates and controllers.

The file is generated from Weblate and should not be hand edited. `ga` is present in `valid-langs.js` and `prettyprint.js`, so it is listed in the language selector as `Irish`.

## Important APIs, Types, and Data Shape

The file is a JSON object with 558 top-level keys. It has 557 string values and one nested `theme.name` object for GUI theme labels. English source text is the ID namespace, while nested IDs such as `theme.name.black` are represented as nested JSON objects.

The catalog is consumed by Angular Translate through the static-files loader configured in `syncthing/app.js`. Translated strings preserve the placeholder contract used by templates and controllers.

## Control Flow, State, and Persistence

`LocaleService` chooses a locale from URL, localStorage, or `/rest/svc/lang`, then calls `$translate.use('ga')` and sets `document.documentElement.lang` to `ga` after loading. GUI markup uses `translate` attributes, translate filters, and JavaScript `$translate.instant(...)` calls to resolve IDs.

The file has no internal state. Explicit language changes are persisted under browser localStorage key `SYN_LANG`; otherwise browser language negotiation supplies the default.

## Dependencies and Integration Points

Runtime dependencies are AngularJS, Angular Translate, `ngSanitize`, `LocaleService`, `languageSelectDirective.js`, `valid-langs.js`, `prettyprint.js`, and static asset serving. Maintenance depends on Weblate plus `script/weblatedl.go` and `script/translate.go`.

## Risks and Test Signals

Irish has full top-level key coverage against `lang-en.json`: zero missing and zero extra keys. Placeholder parity checks found no mismatched placeholder names, reducing risk in interpolated prompts and status messages.

Remaining risks are semantic translation accuracy, generated updates overwriting local edits, and layout overflow from longer strings. Validation signals: `jq -e .` succeeds; size is 52,967 bytes and 567 lines; key count is 558; value distribution is 557 strings and one object; `ga` is registered in `valid-langs.js` and `prettyprint.js`.
