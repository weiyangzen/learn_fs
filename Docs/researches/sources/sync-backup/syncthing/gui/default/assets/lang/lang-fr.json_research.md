# sources/sync-backup/syncthing/gui/default/assets/lang/lang-fr.json

## Purpose

`lang-fr.json` is the French runtime translation catalog for the Syncthing AngularJS web GUI. It maps English source strings used by `translate` attributes, Angular translate filters, and `$translate.instant(...)` calls to French strings. It is loaded on demand as `assets/lang/lang-fr.json` when the selected locale is `fr`.

The language directory README says these files are generated and should not be edited directly; translation updates are expected to flow from Weblate into this JSON asset. `fr` is listed in both `valid-langs.js` and `prettyprint.js`, so the GUI language selector exposes it as `French`.

## Important APIs, Types, and Data Shape

The file is a JSON object with 558 top-level keys. Of those, 557 values are strings and one value is the nested `theme.name` object. The keys are the English message IDs extracted by `script/translate.go`; some include interpolation placeholders like `{%device%}`, `{%folder%}`, and `{%version%}`.

Runtime consumers are the Angular Translate static file loader in `syncthing/app.js`, `LocaleService`, and `languageSelectDirective.js`. `$translateProvider.fallbackLanguage('en')` makes the English catalog the fallback for missing IDs.

## Control Flow, State, and Persistence

`LocaleService.autoConfigLocale()` chooses the locale from `?lang=`, browser localStorage, or `/rest/svc/lang`. If `fr` is selected or negotiated, Angular Translate requests `assets/lang/lang-fr.json`. Templates and controllers then resolve message IDs through the loaded catalog.

The JSON file itself has no mutable state. User language choice is persisted outside the file under localStorage key `SYN_LANG`; after a successful load the document `lang` attribute is set to `fr`.

## Dependencies and Integration Points

Runtime dependencies are AngularJS, `pascalprecht.translate`, the static-files loader, `ngSanitize`, `valid-langs.js`, and `prettyprint.js`. Maintenance integrates with `script/weblatedl.go`, `script/translate.go`, and Weblate as documented by `assets/lang/README.txt`. Static assets under `/assets/` and `/rest/svc/lang` are allowed without auth so language selection works on the login page.

## Risks and Test Signals

French has complete key coverage against `lang-en.json`: zero missing and zero extra top-level keys. Placeholder parity checks found no mismatched placeholder names. Remaining risks are stale generated translations, local edits being overwritten by Weblate refreshes, and translated text length affecting constrained GUI controls.

Validation signals: `jq -e .` succeeds; size is 57,132 bytes and 567 lines; key count is 558; value distribution is 557 strings and one object; `fr` is registered in `valid-langs.js` and `prettyprint.js`.
