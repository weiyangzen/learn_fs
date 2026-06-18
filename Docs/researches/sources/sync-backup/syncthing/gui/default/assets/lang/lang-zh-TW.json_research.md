# sources/sync-backup/syncthing/gui/default/assets/lang/lang-zh-TW.json

## Purpose
This file is the Taiwan Traditional Chinese (`zh-TW`) angular-translate catalog for the Syncthing default web GUI. It localizes the source English strings used across the AngularJS application and acts as the closest Traditional Chinese fallback for some shared behavior, notably duration formatting for Chinese locales.

## Important APIs, types, and data
The artifact is a JSON object with 546 top-level keys. It contains translations for device and folder management, file synchronization status, ignore rules, versioning, connection/discovery settings, upgrade and restart flows, usage reporting, and common action labels. It includes Angular interpolation placeholders and a nested `theme.name` object mapping theme identifiers to localized labels.

## Control flow and integration
The file has no direct control flow. It is fetched by angular-translate when `$translate.use('zh-TW')` is called by `LocaleService`. `valid-langs.js` makes it selectable, `prettyprint.js` supplies the display name, and `durationFilter.js` adds `zh_TW` as a fallback for all `zh-*` duration-language choices. If a translation key is absent here, the app falls back to English.

## State and persistence behavior
The file is a static JSON resource. Locale persistence is handled outside the file through `LocaleService` and `localStorage.SYN_LANG`; the selected language also updates the root HTML `lang` attribute after `$translate.use()` succeeds.

## Dependencies and integration points
Dependencies are angular-translate JSON loading, exact source-string keys from templates/controllers, the global locale lists, and interpolation compatibility. The nested theme translation data integrates with settings/theme UI where object-valued translation keys can be read by angular-translate or direct code paths.

## Risks
Translation catalogs can drift from the English source when UI strings change. Placeholder mismatches in dynamic folder/device messages would be visible to users. Because `durationFilter.js` uses `zh_TW` as a fallback for Chinese locales, regressions in external humanize-duration language support can affect this locale and `zh-HK`. One value contains angle brackets, so rendering paths should be checked for escaping and correct presentation.

## Test signals
Validate JSON, compare key coverage and placeholder parity against English, load the GUI with `?lang=zh-TW`, check language selector ordering/display, and smoke-test folder/device invite messages and duration values. Also verify `theme.name` still covers every theme identifier used by settings templates.
