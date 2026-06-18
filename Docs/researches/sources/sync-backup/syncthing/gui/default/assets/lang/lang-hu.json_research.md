# sources/sync-backup/syncthing/gui/default/assets/lang/lang-hu.json

Purpose: Hungarian translation catalog for the Syncthing default AngularJS GUI. It maps English translation IDs to Hungarian strings loaded when the selected locale is `hu`.

Important APIs/types/functions: the file is loaded by angular-translate's static files loader configured in `gui/default/syncthing/app.js` with the `assets/lang/lang-` prefix and `.json` suffix. It is made selectable by `valid-langs.js`, displayed as Hungarian by `prettyprint.js`, maintained from Weblate by `script/weblatedl.go`, and should track the English IDs extracted by `script/translate.go`.

Data shape and notable entries: the catalog has 551 top-level entries: 550 string translations and one nested `theme.name` object with four theme labels. Keys are English source phrases and values are Hungarian translations. Dynamic placeholders are preserved by variable name; entries using `{%count%}`, `{%device%}`, `{%folder%}`, `{%foldertype%}`, and similar IDs translate them as Angular `{{...}}` expressions without losing variables.

Control flow: when `hu` is selected, Angular requests `assets/lang/lang-hu.json`, merges it into the translation table, and resolves GUI text through `translate` directives, translation filters, and `$translate.instant(...)`. The fallback language is `en`, so untranslated IDs still render as English instead of failing open with raw IDs.

State/persistence behavior: no application state is mutated by this file. It is static generated content served with the GUI. Persistent locale selection and Syncthing configuration live elsewhere; this JSON only contributes display strings.

Dependencies/integration points: depends on AngularJS interpolation syntax, the angular-translate loader, locale registration files, Weblate export format, and the Syncthing GUI source convention where the English phrase is the message ID. The nested `theme.name` namespace is used by theme display code and is produced by the English catalog extraction script's theme collection logic.

Risks: compared with `lang-en.json`, this catalog is missing 7 current keys: `Block Indexing`, `Device Group`, `Folder Group`, `Maintain an index of all blocks in the folder, enabling reuse of blocks from other files when syncing changes. Disable to reduce database size at the cost of not being able to reuse blocks across files.`, `Optional group for the device. Can be different on each device.`, `Optional group for the folder. Can be different on each device.`, and `Starting`. These fall back to English in Hungarian sessions. Other risks are stale terminology around synchronization behavior, string length/layout pressure, and future edits that break JSON typing or placeholders.

Test signals: validate syntax with `jq`; compare key sets against `lang-en.json`; run a placeholder consistency check over both `{%...%}` and `{{...}}`; smoke test the Hungarian GUI in settings, advanced settings, folder edit, device edit, and status views, paying attention to the missing block indexing and group labels.
