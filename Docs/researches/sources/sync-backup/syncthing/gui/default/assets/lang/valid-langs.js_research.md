# sources/sync-backup/syncthing/gui/default/assets/lang/valid-langs.js

## Purpose
This file defines the global `validLangs` array of locale codes that the Syncthing GUI considers available for translation and locale selection.

## Important APIs, types, and functions
The only API is the global variable assignment `var validLangs = [...]`. Values are locale strings matching `lang-<code>.json` filenames and `prettyprint.js` keys. `app.js` declares `validLangs` as a global and passes it into `LocaleServiceProvider.setAvailableLocales(validLangs)` during Angular configuration.

## Control flow and integration
The file has no executable logic beyond creating the array. At runtime, `LocaleService` uses this list for browser-language matching and `languageSelectDirective.js` uses it to decide which language names appear in the dropdown. The order can influence automatic browser-language selection when a short accepted language such as `zh` matches multiple available locales.

## State and persistence behavior
The file is static and stateless. It indirectly affects persisted state because users can only choose listed locales for storage in `SYN_LANG` through the language selector, although URL `?lang=` can still request arbitrary language strings and rely on `$translate` behavior.

## Dependencies and integration points
It must be loaded before Angular app configuration in `app.js`. It should be synchronized with actual translation JSON files and `langPrettyprint` display names. The list integrates with `LocaleServiceProvider`, browser locale matching from `/rest/svc/lang`, and the language dropdown.

## Risks
Adding a locale code without a JSON file creates failed translation loads or English fallback. Omitting an existing catalog makes it unreachable from automatic selection and the dropdown. Ordering can affect generic language prefix matches; for example a browser language of `zh` may select the first Chinese variant present in this array.

## Test signals
Validate each `validLangs` entry has both `assets/lang/lang-<code>.json` and a pretty name. Test automatic language negotiation for exact and prefix matches, and verify the dropdown includes all listed languages without bracket fallback labels.
