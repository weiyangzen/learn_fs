# sources/sync-backup/syncthing/gui/default/assets/lang/lang-id.json

Purpose: Indonesian translation catalog for the Syncthing default AngularJS GUI. It maps English translation IDs to Indonesian strings loaded for locale `id`.

Important APIs/types/functions: the file is consumed by angular-translate via the static file loader configured in `gui/default/syncthing/app.js`. `valid-langs.js` exposes `id` as selectable, `prettyprint.js` labels it Indonesian, `script/weblatedl.go` downloads the Weblate file and writes `lang-id.json`, and `script/translate.go` defines the English catalog generation behavior that this file follows.

Data shape and notable entries: the catalog has 551 top-level entries: 550 string translations and one nested `theme.name` object with Indonesian names for the four bundled themes. English source strings act as IDs. Some entries intentionally remain identical to English, such as protocol abbreviations and several product/about texts. Placeholder variable sets match exactly across source keys and Indonesian values.

Control flow: selecting Indonesian causes the GUI to load `assets/lang/lang-id.json`; angular-translate then resolves translated labels in HTML templates and JavaScript-generated messages. Values with placeholders are interpolated with runtime data such as device names, folder IDs, counts, paths, and versions. Missing translations fall back to English because the app configures `fallbackLanguage('en')`.

State/persistence behavior: this file is static generated UI data and does not store Syncthing runtime state. It is read by the browser as an asset; durable configuration, selected locale, and synchronization state are outside the file.

Dependencies/integration points: depends on AngularJS, angular-translate, locale registration assets, Weblate output, and Syncthing's translation extraction scripts. It integrates with high-visibility GUI surfaces including authentication, settings, folder/device modals, error notifications, usage reporting, crash reporting, share prompts, status tables, and the theme selector.

Risks: compared with `lang-en.json`, this catalog is missing 7 current keys: `Block Indexing`, `Device Group`, `Folder Group`, `Maintain an index of all blocks in the folder, enabling reuse of blocks from other files when syncing changes. Disable to reduce database size at the cost of not being able to reuse blocks across files.`, `Optional group for the device. Can be different on each device.`, `Optional group for the folder. Can be different on each device.`, and `Starting`. Those render in English for Indonesian users. Additional risks include stale security/authentication wording, untranslated English strings that may be intentional but reduce localization quality, and layout overflow in tables or buttons.

Test signals: `jq` parsing should succeed; key comparison against `lang-en.json` should show only the known missing keys; placeholder consistency should remain zero mismatches; browser smoke tests should switch to Indonesian and cover settings, connection status, folder edit advanced options, receive-encrypted warnings, and interpolated share/device prompts.
