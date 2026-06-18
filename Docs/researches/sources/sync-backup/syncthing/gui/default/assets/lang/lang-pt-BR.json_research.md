# sources/sync-backup/syncthing/gui/default/assets/lang/lang-pt-BR.json

## Purpose

`lang-pt-BR.json` supplies Brazilian Portuguese translations for the Syncthing default web GUI. It is generated from Weblate-managed translations and is part of the static frontend assets.

The file is a JSON object with 558 top-level entries, matching `lang-en.json`. It has no missing or extra keys relative to English and no empty string values.

## Important APIs, Types, and Data Shape

The file's API surface is a JSON translation table. It contains 557 top-level string translations and one nested `theme.name` object. The keys are English source phrases from GUI templates/controllers; values are Brazilian Portuguese strings.

Dynamic text uses Angular interpolation in translated values, for example `{{name}}`, `{{device}}`, or `{{folder}}`, while source IDs often contain `{%...%}` placeholders. That transformation is expected by angular-translate and the GUI templates' `translate-value-*` attributes.

The `theme.name` object supplies localized names for theme IDs consumed by `themeName()` in `syncthingController.js`.

## Control Flow and Runtime Use

When the active locale is `pt-BR`, angular-translate loads `assets/lang/lang-pt-BR.json` via the static file loader configured in `syncthing/app.js`. Translations are then used throughout the AngularJS GUI by `translate` directives, filters, tooltip expressions, and `$translate.instant(...)`.

`pt-BR` is present in `valid-langs.js`, so it is available in the language selector and can be selected automatically from matching browser accept-language values returned by `/rest/svc/lang`.

The global fallback language is English. Since this file currently has full English key coverage, fallback should mainly matter if future source strings are added without Brazilian Portuguese translations.

## State and Persistence Behavior

The file is static and immutable at runtime. angular-translate caches the loaded table in memory for the selected locale.

Selection and persistence are handled by `LocaleService`; choosing Brazilian Portuguese can store `SYN_LANG=pt-BR` in browser `localStorage`, and the document's `lang` attribute is updated to `pt-BR` after successful language activation.

## Dependencies and Integration Points

Dependencies include angular-translate, the static files loader, Angular interpolation/sanitization, `valid-langs.js`, and `prettyprint.js` for the user-facing locale name. The file integrates with the full default GUI surface: navigation, settings, device and folder modals, discovery/listener status, file versioning, restore actions, local changes, usage reporting, and warnings.

Its filename is part of the runtime contract: `$translate.use('pt-BR')` maps to `assets/lang/lang-pt-BR.json`.

## Risks

The primary risk is future catalog drift: new English keys without translations will silently fall back to English. Placeholder mistakes are also high impact because they can remove device names, folder IDs, URLs, counts, or other dynamic values from warning and confirmation text.

Eight values are identical to their English keys: `LDAP`, `OK`, `QUIC LAN`, `QUIC WAN`, `Relay LAN`, `Relay WAN`, `TCP LAN`, and `TCP WAN`. These are likely intentionally untranslated acronyms/protocol labels but remain useful review signals.

As generated Weblate output, local manual edits should be avoided.

## Test Signals

Static validation should parse the JSON, compare key sets with `lang-en.json`, assert no missing/extra keys, assert no empty string values, verify the `theme.name` object, and check that interpolation variables remain present in translated strings.

Runtime validation should load the GUI with `?lang=pt-BR`, verify the selector exposes Brazilian Portuguese, confirm `SYN_LANG=pt-BR` persistence, inspect a few interpolated modals and tooltips, and verify localized theme names in the settings dialog.
