# sources/sync-backup/syncthing/gui/default/assets/lang/lang-fa.json

Purpose: Persian/Farsi translation asset placeholder for the Syncthing default web GUI. The file is valid JSON but contains an empty object, so it contributes no translated UI strings.

Important APIs/types/functions: this file is still compatible with angular-translate's static-file loader because it is a JSON object. If requested as `assets/lang/lang-fa.json`, `$translate.use('fa')` can load it, but all actual translation lookups will miss and fall back to English. There are no nested structures such as `theme.name`.

Control flow: normal UI language discovery should not select this file because `fa` is absent from `assets/lang/valid-langs.js` and `prettyprint.js`. Explicit URL language selection or a stale saved locale can still ask the loader for it. Once loaded, every English translation ID is missing and the configured English fallback supplies display text.

State and persistence behavior: no data state, no local persistence, and no runtime mutation. External locale persistence remains `LocaleService` responsibility through `SYN_LANG`.

Dependencies and integration points: present in the same generated language directory as complete and partial translations, so build packaging may include it even though the GUI does not advertise it. Its empty content suggests either a translation below publication threshold, a stale generated artifact, or a placeholder retained by the sync-backup source snapshot.

Risks: if directly selected, it creates an English UI while `document.documentElement.lang` may be set to `fa`, which can mislead assistive technology, browser spell/typography behavior, and user expectations. It provides no right-to-left translated strings and no theme names. Since no interpolation strings exist, interpolation corruption is not a direct risk.

Test signals: `jq` parses the file as an object; key count is 0; it is missing all 558 English baseline keys; no extra keys or empty string values; `valid-langs.js` does not include `fa`.
