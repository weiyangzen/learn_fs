# sources/sync-backup/syncthing/gui/default/assets/lang/lang-cs.json

Purpose: provides Czech translations for Syncthing's default AngularJS web GUI. It is a static translation table loaded as `assets/lang/lang-cs.json` when the selected or negotiated locale is `cs`, displayed as `Czech` by the locale UI.

Important APIs/types/functions: this is JSON data, not executable code. It follows the same `translation map[string]any` structure consumed by Syncthing's translation scripts: flat English strings map to Czech values, and the nested `theme.name` object maps theme identifiers to Czech display names. Interpolation-bearing strings preserve Angular placeholders such as `{{name}}`, `{{label}}`, `{{count}}`, `{{device}}`, and `{{folder}}`.

Control flow: `app.js` registers the static translation loader and English fallback. `LocaleService` can choose `cs` from `?lang=cs`, saved localStorage, or `/rest/svc/lang` browser preferences because `cs` is listed in `valid-langs.js`. Once selected, Angular templates and controller code resolve translation IDs against this file. Missing Czech entries are resolved through the English fallback.

State and persistence behavior: the JSON file is static and read-only at runtime. Browser locale choice may be persisted under `SYN_LANG`; `LocaleService.useLocale()` also sets the root HTML `lang` attribute to `cs` after the translation table loads. Source updates flow from Weblate via `script/weblatedl.go` and from source-key extraction via `script/translate.go`.

Dependencies and integration points: integrated with `valid-langs.js` (`cs` is available) and `prettyprint.js` (`cs` is named `Czech`). It depends on `angular-translate` static-file loading, Syncthing HTML translate directives, JavaScript `$translate.instant(...)` keys, and generated theme-name collection from GUI theme directories.

Risks and edge cases: this locale has 520 flattened entries, 41 fewer than `lang-en.json`. Missing items include some recent or specialized UI strings such as `Block Indexing`, `Folder Group`, `Folder Status`, `Limit Bandwidth in LAN`, several connection-type labels (`QUIC LAN`, `Relay WAN`, `TCP LAN`), and newer share text that interpolates `{%devicename%}`. Placeholder integrity is good in the inspected file: all 21 placeholder-bearing entries preserve matching placeholder names. Four values are identical to their keys, which may indicate untranslated technical terms. Because missing entries fall back to English, mixed-language screens are the likely failure mode rather than hard errors.

Test signals: `python3 -m json.tool` parses the file successfully. A structural check found 517 top-level keys, 520 flattened leaves, nested `theme.name`, no empty values, and no placeholder mismatches. Practical tests should select `?lang=cs`, verify common settings/device/folder views render Czech strings, verify fallback for an intentionally missing key, and exercise interpolation-heavy dialogs such as removing a device or sharing a folder.
