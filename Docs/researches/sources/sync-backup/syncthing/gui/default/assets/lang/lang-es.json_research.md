# sources/sync-backup/syncthing/gui/default/assets/lang/lang-es.json

Purpose: Spanish translation table for the Syncthing default web GUI. The file maps English message IDs to Spanish UI text and is loaded at runtime as `assets/lang/lang-es.json`.

Important APIs/types/functions: the file itself is a JSON object, not executable code. It is consumed by AngularJS `pascalprecht.translate` through `$translateProvider.useStaticFilesLoader({prefix: 'assets/lang/lang-', suffix: '.json'})` in `gui/default/syncthing/app.js`. Locale selection flows through `LocaleService.useLocale`, `$translate.use(language)`, and `document.documentElement.lang`. The nested `theme.name` object supports `$translate.instant("theme.name." + theme)` in `syncthingController.js`.

Control flow: `valid-langs.js` advertises `es`, browser or saved locale selection chooses it, angular-translate fetches this JSON, then templates, filters, directives, and controller calls resolve English source strings to Spanish strings. Missing keys would fall back to English because app configuration sets `$translateProvider.fallbackLanguage('en')`.

State and persistence behavior: the translation table is static, generated data. It does not persist application state. The selected language can be stored under `SYN_LANG` in localStorage when selected through a save path, and the loaded table is cached by angular-translate during the page lifetime.

Dependencies and integration points: generated from the upstream translation workflow described by `assets/lang/README.txt`; integrated with `valid-langs.js`, `prettyprint.js`, the Angular translation loader, and all UI views using English literals as translation IDs. The file has 558 top-level keys, matching `lang-en.json` with no missing or extra keys. Its only non-string top-level value is `theme`, an object with `black`, `dark`, `default`, and `light` names.

Risks: Spanish is exposed in `valid-langs.js`, so any invalid JSON blocks a selectable UI language. Interpolated values must preserve Angular variable names from keys such as `{%device%}` as `{{device}}`; checked entries preserve their slots. A small number of values intentionally remain the same as English for protocol labels or short words, but that can also hide untranslated strings.

Test signals: `jq` parses the file as an object; key count equals the English baseline; no missing or extra keys; no empty string values; placeholder scan found no key/value slot mismatches; `valid-langs.js` includes `es`.
