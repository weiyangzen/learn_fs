# sources/sync-backup/syncthing/gui/default/syncthing/core/languageSelectDirective.js

## Purpose
This directive renders the language selector dropdown and connects user language changes to `LocaleService`.

## Important APIs, types, and functions
It registers `languageSelect` as element/attribute directive. Its inline template renders a Bootstrap dropdown with a globe icon, current locale display name, and one menu item per available locale. The link function reads `LocaleService.getAvailableLocales()`, `getLocalesDisplayNames()`, `getCurrentLocale()`, and calls `LocaleService.useLocale(locale, true)` when the user selects a language.

## Control flow
The directive filters display names to locales that are actually available, falling back to `[code]` labels when a pretty name is missing. It inverts the code-to-name object into name-to-code, sorts names alphabetically, and shows the dropdown only when English is present. A `$watch` waits for `LocaleService.getCurrentLocale` to become truthy because `LocaleService.autoConfigLocale()` may select a locale asynchronously after `/svc/lang`; once found, it sets `$scope.currentLocale` and removes the watcher. `changeLanguage()` persists the selected locale and updates the local current-locale state.

## State and persistence behavior
Directive scope stores `localesNames`, inverted maps, sorted names, `visible`, and `currentLocale`. Persistence is delegated to `LocaleService.useLocale(locale, true)`, which writes `SYN_LANG` when local storage is available.

## Dependencies and integration points
It depends on Bootstrap dropdown markup/classes, Font Awesome globe icon classes, `LocaleService`, global locale metadata consumed by that service, and Angular scope watching. It integrates with `prettyprint.js` and `valid-langs.js` through the service provider configuration.

## Risks
Inverting by display name loses entries when two locales share the same display name. The initial watcher removes itself on the first truthy current locale, so external later changes must also update `$scope.currentLocale` through `changeLanguage()` or re-render. Missing English hides the selector. The template uses `href="#"`; click handlers rely on Angular/Bootstrap behavior to avoid unwanted navigation.

## Test signals
Unit tests should cover missing pretty names, duplicate display names, initial async locale selection, `changeLanguage()` persistence calls, and visibility when `en` is absent. Browser tests should verify dropdown ordering, active class assignment, and selected locale display.
