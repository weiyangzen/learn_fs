# sources/sync-backup/syncthing/gui/default/syncthing/core/localeService.js

## Purpose
This provider owns GUI locale selection for Syncthing: available/default locale configuration during app bootstrap, automatic locale detection, explicit locale changes, translation activation, HTML language attribute updates, and optional persistence in local storage.

## Important APIs, types, and functions
The provider exposes `setDefaultLocale(locale)` and `setAvailableLocales(locales)` during config. The runtime service exposes `autoConfigLocale()`, `useLocale(language, save2Storage)`, `getCurrentLocale()`, `getAvailableLocales()`, and `getLocalesDisplayNames()`. Internal helpers include `detectLocalStorage()`, `readBrowserLocales()`, and `autoConfigLocale()`'s matching loop. The storage key is the constant string `SYN_LANG`.

## Control flow
Provider construction feature-detects `window.localStorage` by writing and removing a temporary key. `autoConfigLocale()` first checks `$location.search().lang`; if present, it immediately uses and persists that locale. Otherwise it checks saved `SYN_LANG`; if present, it uses it without rewriting. If neither exists, it calls `GET rest/svc/lang` and scans the returned browser-language preferences. For each language, it finds available locales whose lower-case code starts with the browser language and either exactly matches or has a hyphen separator after the prefix. The first match wins; otherwise the configured default locale is used. `useLocale()` calls `$translate.use(language).then(...)`, sets `document.documentElement.lang`, and writes `SYN_LANG` when requested and storage is available.

## State and persistence behavior
Provider-level state holds `_defaultLocale`, `_availableLocales`, and `_localStorage`. Runtime state is mostly managed by `$translate`; this service reads from and writes to that state. Persistent browser state is optional `localStorage.SYN_LANG`. The root document `lang` attribute is mutable UI/document state and updates only after translation loading succeeds.

## Dependencies and integration points
Dependencies include `$http`, `$translate`, `$location`, global `urlbase`, global `langPrettyprint`, browser `window.localStorage`, and `document.documentElement`. `app.js` configures available/default locales. `languageSelectDirective.js` reads current/available/display names and calls `useLocale()`. `durationFilter.js` reads `$translate.use()` separately, so locale selection here influences duration formatting.

## Risks
URL `?lang=` accepts any string and passes it to `$translate.use`; missing catalog behavior depends on angular-translate fallback/loading errors. The browser-language match depends on order in `valid-langs.js`, so generic prefixes can select an unintended regional variant. Local-storage access can be unavailable and is correctly guarded, but persistence silently disappears in private/restricted environments. Since `useLocale()` writes storage only after `$translate.use()` resolves, failed catalog loads do not persist but may leave the current locale unchanged.

## Test signals
Mock `$http`, `$translate`, `$location`, and localStorage to cover precedence order (`?lang`, saved value, browser list, default), prefix matching boundaries, unavailable storage, successful persistence, root `lang` attribute updates, and missing/failed language loads. Integration tests should verify `rest/svc/lang` negotiation and language selector changes.
