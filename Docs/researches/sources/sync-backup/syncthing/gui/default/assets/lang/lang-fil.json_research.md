# sources/sync-backup/syncthing/gui/default/assets/lang/lang-fil.json

Purpose: Filipino translation table for the Syncthing default web GUI. It maps English message IDs to Filipino UI text and is advertised as a selectable GUI language.

Important APIs/types/functions: generated JSON object loaded by angular-translate's static file loader. Runtime consumers are `$translate.use`, translation directives/filters in HTML, and direct `$translate.instant` calls. The nested `theme.name` object supports localized theme display names.

Control flow: `valid-langs.js` includes `fil`, so browser negotiation, the language picker, a saved locale, or `?lang=fil` can select it. The loader fetches `assets/lang/lang-fil.json`; present IDs render Filipino text and the small missing set falls back to English.

State and persistence behavior: no mutable state in the file. Locale preference can be persisted in localStorage under `SYN_LANG`, and angular-translate can cache the loaded table during a session.

Dependencies and integration points: generated from Weblate/translation tooling and paired with `prettyprint.js` for display name `Filipino`. It has 551 top-level keys, no extra keys, and is missing 7 English baseline keys. The only non-string top-level value is `theme`, with the four expected theme names.

Risks: because it is selectable, the 7 missing keys create visible English fallback for specific newer UI concepts such as block indexing and optional device/folder groups. Some values intentionally remain identical to English, especially technical labels; that is valid for names like API terms but can mask untranslated text. Present interpolation slots match their keys.

Test signals: `jq` parses the file as an object; `valid-langs.js` includes `fil`; no extra keys; 7 missing keys versus English; no empty string values; placeholder scan found no key/value slot mismatches; theme names are present.
