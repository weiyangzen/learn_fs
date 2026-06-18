# sources/sync-backup/syncthing/gui/default/assets/lang/lang-fi.json

Purpose: Finnish translation table for the Syncthing default web GUI. It maps English message IDs to Finnish UI text, but the current asset is partial and not advertised in the active locale list.

Important APIs/types/functions: generated JSON object consumed by the angular-translate static-file loader configured in `app.js`. Locale control flows through `LocaleService` and `$translate`. The file includes a nested `theme.name` object used by controller-side theme display lookups.

Control flow: `fi` is not listed in `valid-langs.js`, so normal language discovery and picker display should not choose it. Explicit `?lang=fi` or a saved `SYN_LANG=fi` can still cause `$translate.use('fi')` to load it. Present keys render Finnish strings; missing keys fall back to English.

State and persistence behavior: static translation data with no direct writes. The only persistence related to it is the user's selected locale in localStorage, handled by `LocaleService`.

Dependencies and integration points: tied to the English key set and translation generator. It has 418 top-level keys, no extra keys, and is missing 140 English baseline keys. The only non-string top-level value is `theme`, with all four expected theme names.

Risks: direct use produces a mixed Finnish/English UI due to missing keys. The file is not in `valid-langs.js`, so it may be intentionally below completion threshold or stale; updating only this file without regenerating `valid-langs.js` would not make it selectable. Placeholder checks on present strings pass, so the largest functional risk is coverage, not runtime expression failure.

Test signals: `jq` parses the file as an object; no extra keys; 140 missing keys versus `lang-en.json`; no empty string values; placeholder scan found no key/value slot mismatches; `valid-langs.js` does not include `fi`; `theme.name` has `black`, `dark`, `default`, and `light`.
