# sources/sync-backup/syncthing/gui/default/assets/lang/lang-fr-CA.json

Purpose: Canadian French translation table for the Syncthing default web GUI. It maps English message IDs to French Canadian UI text, but the snapshot is partial and not advertised in the active locale list.

Important APIs/types/functions: generated JSON object consumable by angular-translate. The surrounding APIs are the static-file loader in `app.js`, `LocaleService.useLocale`, `$translate.use`, template translation directives, filters, and direct controller translations. This file has no nested `theme.name` object.

Control flow: `fr-CA` is absent from `valid-langs.js`, so normal language discovery will not expose it. Explicit selection can still load `assets/lang/lang-fr-CA.json`. Present keys translate, while missing keys fall back to English. Since no `theme.name` object exists, theme-name lookups fall back to controller title-casing.

State and persistence behavior: static translation data only. User locale persistence, if any, is external in the `SYN_LANG` localStorage value.

Dependencies and integration points: shares the generated language directory with `lang-fr.json`, which is the advertised French locale. It has 240 top-level keys, no extra keys, and is missing 318 English baseline keys. The file covers many older/common GUI labels but omits a large portion of newer interface text.

Risks: direct use results in a heavily mixed French Canadian/English UI and `document.documentElement.lang=fr-CA` despite incomplete translation coverage. Because the locale is not advertised, the file may be stale or below inclusion threshold. Present interpolation slots match, so partial coverage and absent theme names are the primary risks.

Test signals: `jq` parses the file as an object; no extra keys; 318 missing keys versus `lang-en.json`; no empty string values; placeholder scan found no key/value slot mismatches; `valid-langs.js` does not include `fr-CA`; no `theme.name` object.
