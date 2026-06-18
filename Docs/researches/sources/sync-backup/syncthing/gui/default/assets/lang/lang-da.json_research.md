# sources/sync-backup/syncthing/gui/default/assets/lang/lang-da.json

Purpose: provides Danish translations for Syncthing's default AngularJS web GUI. It is loaded as `assets/lang/lang-da.json` for the `da` locale and lets the GUI present Danish labels, help text, warnings, and dialog copy.

Important APIs/types/functions: the file is a JSON translation dictionary with English source strings as lookup keys. It includes 549 flattened translation leaves and the nested `theme.name` namespace for theme labels. Placeholder-bearing translations preserve Angular interpolation variables, including device/folder names and counts, by translating `{%...%}` source placeholders into matching `{{...}}` placeholders in values.

Control flow: Syncthing configures `$translateProvider.useStaticFilesLoader()` with the `assets/lang/lang-` prefix and `.json` suffix, then uses `LocaleService` to select `da` from query parameter, saved `SYN_LANG`, or browser locale negotiation. The selected language table is used by Angular translation directives and filters across core, device, folder, settings, and modal views. English fallback remains active for untranslated Danish keys.

State and persistence behavior: the file is static; mutable language state lives in browser localStorage and the `$translate` service. If explicitly chosen, `da` can be saved as `SYN_LANG`, and the document `lang` attribute is set to `da` after successful loading. Generation and maintenance are handled by Weblate download and source extraction scripts, not by runtime code.

Dependencies and integration points: `da` is present in `valid-langs.js` and mapped to `Danish` in `prettyprint.js`. It integrates with AngularJS, `pascalprecht.translate`, `ngSanitize`, Syncthing's `/rest/svc/lang` locale discovery endpoint, and the translation extraction path that scans templates, JavaScript, and theme directories.

Risks and edge cases: Danish coverage is high but not complete: 12 English entries are absent, including `Block Indexing`, `Device Group`, `Folder Group`, `Limit Bandwidth in LAN`, and folder-type constraint messages such as `Always turned on when the folder type is "{%foldertype%}".` There are 11 values equal to their source key, likely technical labels or untranslated remnants. The inspected 23 placeholder-bearing entries have no placeholder mismatches, reducing the risk of broken interpolation in dialogs. Missing keys should fall back to English, resulting in isolated mixed-language strings.

Test signals: `python3 -m json.tool` parses the file successfully. Structural checks found 546 top-level keys, 549 flattened leaves, nested `theme.name`, no empty values, and zero placeholder mismatches. UI smoke tests should select `?lang=da`, inspect the settings/device/folder modals, verify theme names render, and test interpolation in remove/share/restore confirmation dialogs.
