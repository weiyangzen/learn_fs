# sources/sync-backup/syncthing/gui/default/assets/lang/lang-zh-HK.json

## Purpose
This file is the Hong Kong Traditional Chinese (`zh-HK`) angular-translate catalog for Syncthing's default GUI. It provides localized UI text for the same source-string based translation system as other language catalogs and is selected when the locale resolver or explicit language selector chooses `zh-HK`.

## Important APIs, types, and data
The artifact is a JSON object with 501 top-level keys. It translates core GUI labels, status strings, folder/device actions, validation messages, usage-report wording, modal titles, and share-invitation text. Like the other catalogs, keys are English source strings and values are localized strings. It contains interpolation values such as `{{device}}`, `{{folder}}`, and `{{folderlabel}}`; the source keys for those entries still use `{%...%}` marker text. Compared with `zh-CN` and `zh-TW`, this catalog has fewer keys, so it likely relies more often on English fallback for newer UI strings.

## Control flow and integration
The file has no executable logic. `app.js` registers the static loader, and `LocaleService` can select `zh-HK` either from the `lang` query parameter, saved `SYN_LANG`, or browser-language negotiation. `durationFilter.js` treats all Chinese language codes specially by adding `zh_TW` as a humanize-duration fallback; this matters for `zh-HK` because the duration library may not have a dedicated Hong Kong locale.

## State and persistence behavior
The JSON file is static and stateless. The selected locale can be persisted in browser local storage by `LocaleService.useLocale(locale, true)`, but the catalog itself does not write state. Browser/server caching can affect update visibility after translation changes.

## Dependencies and integration points
The catalog depends on angular-translate, the static asset naming convention `lang-<locale>.json`, `valid-langs.js` listing `zh-HK`, and `prettyprint.js` providing its display name. Runtime callers depend on exact key strings and matching placeholders. Because Hong Kong terminology differs from Taiwan terminology, this file is intentionally distinct from `zh-TW` even though `durationFilter.js` may use a `zh_TW` fallback for duration units.

## Risks
The reduced key count creates a higher mixed-language risk. Missing or inconsistent punctuation/placeholder names can make dynamic invite strings awkward or wrong. A translation with embedded angle brackets exists, so sanitization and escaping should be verified for the relevant UI path. Browser language matching in `LocaleService` compares lower-case server-provided accepted languages to lower-case available locales; if the backend provides only `zh` rather than `zh-hk`, it may select the first matching Chinese variant by order instead of this file.

## Test signals
Run JSON validation, compare key coverage against `lang-en.json`, and perform placeholder parity checks. In-browser smoke tests should open `?lang=zh-HK`, verify the language selector label, confirm share invitations interpolate names correctly, and check duration displays for `zh-HK` because that path relies on the Chinese fallback behavior in `durationFilter.js`.
