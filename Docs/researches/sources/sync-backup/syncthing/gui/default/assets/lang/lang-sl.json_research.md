# sources/sync-backup/syncthing/gui/default/assets/lang/lang-sl.json

## Purpose
`lang-sl.json` is the Slovenian translation catalog for the Syncthing default web GUI. It maps English UI message IDs to Slovenian display strings consumed by AngularJS `translate` directives, the `translate` filter, and `$translate.instant(...)` calls throughout `gui/default`.

## APIs, types, and data shape
This file exports no code symbols. Its API is a flat JSON object whose keys are canonical English message IDs and whose values are translated strings. Interpolation placeholders appear in keys as `{%name%}` style tokens and in values as Angular interpolation tokens such as `{{name}}`; the parsed catalog contains 460 keys against 558 English base keys, about 82.4% coverage. There are no extra keys, no empty translations, and no placeholder-token mismatches in the parsed data.

## Control flow
At runtime the GUI language path is selected by `LocaleService.useLocale(language, save2Storage)`, which delegates to `$translate.use(language)`. Once loaded, Angular's translate directive/filter resolves literal text from templates and controller strings against this JSON table. Missing Slovenian keys fall back through the translation subsystem rather than through logic in this file.

## State and persistence behavior
The JSON file is static build-time data. It does not persist user state. The selected locale is persisted separately in browser `localStorage` under `SYN_LANG` by `LocaleService`, and the active document language is reflected through `document.documentElement.lang`.

## Dependencies and integration points
The file depends on the English source keys remaining stable and on Angular Translate's interpolation behavior. `valid-langs.js` includes `sl`, so this locale is expected to be selectable in the language menu. The adjacent `README.txt` states these language files are generated from Weblate and should not be hand-edited directly.

## Risks
The main risk is incomplete catalog coverage: 98 English keys are missing, including newer filtering, connection-management, block-indexing, authentication, and debug/status labels. A GUI path that reaches those strings will display fallback English. Some translated values include trailing spaces or wording issues, but structurally the catalog is parseable and interpolation-safe.

## Test signals
Useful checks are `jq empty lang-sl.json`, key-diff coverage against `lang-en.json`, placeholder set comparison between each key and translated value, and a GUI smoke test selecting Slovenian from the language menu and opening device, folder, settings, log, and notification dialogs.
