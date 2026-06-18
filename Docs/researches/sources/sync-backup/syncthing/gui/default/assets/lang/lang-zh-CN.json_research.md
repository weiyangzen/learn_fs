# sources/sync-backup/syncthing/gui/default/assets/lang/lang-zh-CN.json

## Purpose
This file is the Simplified Chinese (`zh-CN`) angular-translate catalog for the Syncthing default web GUI. It maps English source strings used by templates, controllers, notifications, modal text, form labels, validation messages, and status descriptions to Simplified Chinese translations. It is loaded dynamically by the app-level `$translateProvider` static files loader from `assets/lang/lang-zh-CN.json` when `LocaleService` or URL/local-storage/browser negotiation selects `zh-CN`.

## Important APIs, types, and data
The artifact is a JSON object with 558 top-level translation keys. Keys are mostly English UI strings, including interpolation placeholders such as `{{device}}`, `{{folder}}`, and `{{reintroducer}}`, plus some legacy source strings containing `{%device%}` while the translated value uses Angular interpolation. One nested object appears under `theme.name`, with localized theme labels for `black`, `dark`, `default`, and `light`. The catalog includes operational domains such as devices, folders, ignores, versioning, upgrade/restart flows, discovery/listener status, usage reporting, notification acknowledgement, and advanced settings.

## Control flow and integration
There is no executable control flow in the file; runtime behavior comes from angular-translate. `app.js` configures the loader prefix/suffix, `LocaleService` selects the language, and templates/controllers ask `$translate` to resolve source keys. When a key is missing from this catalog, the app falls back to English because `$translateProvider.fallbackLanguage('en')` is configured. `languageSelectDirective.js` exposes `zh-CN` when the global `validLangs` list contains it and displays its English display name from `prettyprint.js`.

## State and persistence behavior
The catalog does not persist state. Language choice can be persisted by `LocaleService` in `localStorage.SYN_LANG`; the JSON file is a static asset fetched by the browser and may be cached by the web server or browser cache. Translation completeness affects displayed UI state but does not modify Syncthing configuration.

## Dependencies and integration points
Primary dependencies are angular-translate's static files loader, `$translate.use('zh-CN')`, `valid-langs.js`, `prettyprint.js`, and all templates/controllers whose literal English keys must exactly match this file. The file also depends on placeholder compatibility with Angular interpolation: translated strings must preserve the variable names expected by the call site.

## Risks
Missing keys silently degrade to English, producing mixed-language UI. Placeholder mismatches can break dynamic messages or display raw variables. HTML-bearing translations are especially sensitive because translation sanitization is configured to escape values; any intended markup must match existing template behavior. This file has one value containing angle brackets, so sanitation and rendering should be checked when editing. Because the source keys are English prose, upstream wording changes can orphan existing translations even when the Chinese text is still conceptually valid.

## Test signals
Useful checks are JSON parsing, diffing key coverage against `lang-en.json`, validating interpolation placeholders per key, selecting `?lang=zh-CN` in the GUI, and smoke-testing dialogs for device/folder share invitations, upgrade warnings, notification acknowledgements, and advanced settings. Automated tests can assert the file is listed in `valid-langs.js`, named in `prettyprint.js`, and contains no invalid JSON or duplicate keys after generation.
