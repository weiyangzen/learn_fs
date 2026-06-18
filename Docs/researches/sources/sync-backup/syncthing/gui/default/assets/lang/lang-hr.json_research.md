# sources/sync-backup/syncthing/gui/default/assets/lang/lang-hr.json

Purpose: Croatian translation catalog for the Syncthing default AngularJS GUI. It maps English translation IDs to Croatian UI strings loaded at runtime when the active locale is `hr`.

Important APIs/types/functions: the file is a JSON object consumed by `angular-translate` through `$translateProvider.useStaticFilesLoader({ prefix: 'assets/lang/lang-', suffix: '.json' })` in `gui/default/syncthing/app.js`. It is included in `valid-langs.js` as `hr`, named in `prettyprint.js` as Croatian, downloaded by `script/weblatedl.go`, and aligned with the English source catalog maintained by `script/translate.go`.

Data shape and notable entries: the catalog has 558 top-level entries, matching `lang-en.json`: 557 string translations and one nested `theme.name` object containing `black`, `dark`, `default`, and `light`. Translation IDs are English UI source strings. Placeholder-bearing entries preserve the same variable names between keys and values, using translated strings with Angular interpolation such as `{{foldertype}}`.

Control flow: the GUI language service can choose `hr` from the valid locale list. Angular then fetches `assets/lang/lang-hr.json`, registers it with angular-translate, and applies translations from templates, filters, and `$translate.instant(...)`. Missing keys would fall back to English, but no key gaps were found against the checked English catalog.

State/persistence behavior: this file is immutable runtime asset data from the GUI's perspective. It stores no user state and performs no IO beyond being served to the browser. Upstream state is Weblate translation content pulled into the repository by the generation scripts.

Dependencies/integration points: depends on the Angular translation stack, GUI templates/controllers, locale availability files, Weblate-generated JSON, and the theme selector's nested namespace lookup. It is also indirectly tied to build scripts because `build.go` refreshes only the English source catalog, while `weblatedl.go` refreshes translated catalogs and locale indexes.

Risks: the catalog is structurally complete against English, so the main risks are semantic drift from changed GUI behavior, mistranslated operational/security text, placeholder corruption in future edits, and long Croatian strings overflowing narrow controls. The nested `theme` object must remain an object; flattening or stringifying it would break theme name lookups.

Test signals: `jq` should parse the file; key diff against `lang-en.json` should be empty; placeholder variable comparison should report no mismatches; UI smoke coverage should switch to Croatian and exercise dialogs with interpolation, including device/folder share prompts, folder type warnings, and theme names.
