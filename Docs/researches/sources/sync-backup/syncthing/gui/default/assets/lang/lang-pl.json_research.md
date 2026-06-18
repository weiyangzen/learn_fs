# sources/sync-backup/syncthing/gui/default/assets/lang/lang-pl.json

## Purpose

`lang-pl.json` supplies Polish translations for the Syncthing default web GUI. It is generated from the project's Weblate translation pipeline and represents a complete locale catalog for this snapshot.

The file is a JSON object with 558 top-level entries, matching `lang-en.json`. It has no missing or extra keys relative to English and no empty string values.

## Important APIs, Types, and Data Shape

This is static data rather than executable code. The top-level API is the translation dictionary consumed by angular-translate. It contains 557 string phrase mappings plus the nested `theme.name` object for theme display names.

The string keys are English source phrases used in templates and JavaScript. Values are Polish translations, with Angular interpolation syntax (`{{name}}`, `{{folder}}`, etc.) where dynamic values are needed. The nested `theme.name` object maps theme identifiers to Polish names such as black, dark, default, and light equivalents.

## Control Flow and Runtime Use

When `LocaleService` selects Polish, `$translate.use('pl')` causes angular-translate's static file loader to fetch `assets/lang/lang-pl.json`. Translated values then populate all `translate` directives, filter calls, and `$translate.instant(...)` calls that use English source phrases as IDs.

`valid-langs.js` includes `pl`, so Polish participates in the language dropdown and in automatic matching from `/rest/svc/lang`. Missing-key fallback is still configured globally to English, but this catalog currently matches English key coverage.

`themeName()` uses `theme.name.*` through `$translate.instant`. Because this file defines `theme.name`, theme labels should be localized instead of falling back to title-cased raw IDs.

## State and Persistence Behavior

The JSON file itself has no state. After successful loading, angular-translate keeps the Polish table in memory.

The active language is managed by `LocaleService`: a user selection can be stored as `SYN_LANG=pl` in browser `localStorage`, and the document language is set to `pl`. Those persistence behaviors are external to the JSON but depend on this file loading successfully.

## Dependencies and Integration Points

The file depends on the frontend's translation infrastructure: `pascalprecht.translate`, `angular-translate-loader-static-files`, Angular interpolation, `valid-langs.js`, and `prettyprint.js` for display names. It integrates with most user-facing GUI areas, including device management, folder configuration, advanced settings, networking/discovery status, file version restore flows, usage reporting, and warnings.

The filename must remain aligned with locale code `pl`, because the loader constructs the URL from the locale string.

## Risks

The main maintenance risk is placeholder drift when English source phrases change. Dynamic values must keep compatible Angular interpolation variables in the Polish value. Because fallback uses English, any future missing key will produce mixed-language UI rather than a hard failure.

Nine values are identical to their English keys: `Folder`, `GUI`, `LDAP`, `OK`, `QUIC LAN`, `QUIC WAN`, `TCP LAN`, `TCP WAN`, and lowercase `folder`. Most are acronyms, protocol labels, or terms that may intentionally be unchanged, but they are useful review signals.

Because the file is generated, direct local edits can be overwritten by the Weblate update flow.

## Test Signals

Static tests should parse with `jq`, assert 558 keys against `lang-en.json`, assert zero missing and zero extra keys, assert no empty strings, and verify the `theme.name` object is present.

Runtime smoke tests should load `?lang=pl`, check that Polish is visible in the language dropdown, confirm `SYN_LANG=pl` persistence after selection, verify representative interpolated strings render with dynamic values, and inspect the GUI theme selector for Polish theme names.
