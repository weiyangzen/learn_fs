# sources/sync-backup/syncthing/gui/default/assets/lang/lang-et.json

Purpose: Estonian translation table for the Syncthing default web GUI. It maps English message IDs to Estonian UI text, but is currently a partial generated asset.

Important APIs/types/functions: the file is a JSON object consumed by angular-translate's static-file loader from `gui/default/syncthing/app.js`. Runtime consumers include `$translate.use(language)`, translation directives and filters in the GUI, and controller lookups such as `$translate.instant("theme.name." + theme)`. The nested `theme.name` object provides localized theme names.

Control flow: if a caller explicitly requests `et`, angular-translate can fetch `assets/lang/lang-et.json`; however `et` is not present in `assets/lang/valid-langs.js`, so normal browser negotiation and the language picker should not advertise it. If loaded anyway, missing translation IDs fall back to English through the configured fallback language.

State and persistence behavior: static generated data only. The asset does not store Syncthing configuration, device state, or folder state. Locale preference persistence is handled outside the file by `LocaleService` via the `SYN_LANG` localStorage key.

Dependencies and integration points: depends on the translation generation pipeline that also writes `valid-langs.js` and `prettyprint.js`. It has 488 top-level keys, all of which are known English IDs, but it is missing 70 English baseline keys. The only non-string top-level value is `theme`, with `black`, `dark`, `default`, and `light` names.

Risks: because the file is not advertised in `valid-langs.js`, it may be a stale or intentionally unlisted translation. Direct `?lang=et` use or a persisted `SYN_LANG=et` value could still load it, producing a mixed Estonian/English UI because of the 70 missing keys. Slot preservation is intact for present interpolated strings, so the main runtime risk is incompleteness rather than malformed interpolation.

Test signals: `jq` parses the file as an object; no extra keys relative to English; 70 missing keys relative to `lang-en.json`; no empty string values; placeholder scan found no key/value slot mismatches; `valid-langs.js` does not include `et`.
