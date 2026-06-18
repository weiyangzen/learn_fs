# sources/sync-backup/syncthing/gui/default/assets/lang/lang-ckb.json

Purpose: nominally represents the Central Kurdish (`ckb`) Syncthing GUI locale, but the current file is an empty JSON object. As data, it provides no translations and therefore cannot localize the GUI on its own.

Important APIs/types/functions: the file still conforms to the translation-file type expected by the loader: a JSON object decodable as `map[string]any`. It has no flat translation entries, no nested `theme.name` namespace, and no interpolation placeholders.

Control flow: if `$translate.use('ckb')` is ever called, the static file loader can fetch and parse this file, but every UI lookup misses in the selected language. `angular-translate` then uses the configured fallback language `en`, so the user-visible GUI should remain English rather than showing raw missing keys. In the normal Syncthing language picker path, `ckb` is not listed in `valid-langs.js` and not named in `prettyprint.js`, so it should not be automatically selected from browser negotiation or shown as an available language by `LocaleService`.

State and persistence behavior: the file has no translation state. If a user manually forces `?lang=ckb`, `LocaleService.useLocale(language, true)` can persist `SYN_LANG=ckb` after `$translate.use('ckb')` resolves. That creates a persistent preference for an effectively English UI until the language is changed or localStorage is cleared.

Dependencies and integration points: uses the same `assets/lang/lang-<locale>.json` loader convention as the other locale files, but it is currently disconnected from the supported-locale metadata because `ckb` is absent from `valid-langs.js` and `prettyprint.js`. The Weblate downloader normally filters languages by translation completion and current validity; this empty file looks like a leftover or staged locale artifact rather than an enabled locale.

Risks and edge cases: the main risk is accidental enablement. Adding `ckb` to `valid-langs.js` before translations exist would present a language option that localizes nothing. Because the file is syntactically valid and fetchable, loader-level tests may pass while user-visible coverage is effectively zero. Manual `?lang=ckb` selection can also persist an unsupported language key in `SYN_LANG`.

Test signals: `python3 -m json.tool` parses the file successfully, but it contains 0 top-level keys and 0 flattened leaves compared with 561 flattened English entries. Test coverage should assert that unsupported empty locales are not advertised in the language picker and that manually forcing the locale falls back cleanly to English without console loader or interpolation errors.
