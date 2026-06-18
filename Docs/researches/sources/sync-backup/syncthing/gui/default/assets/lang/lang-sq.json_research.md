# sources/sync-backup/syncthing/gui/default/assets/lang/lang-sq.json

## Purpose
`lang-sq.json` is the Albanian translation catalog for the Syncthing default web GUI. It provides a small set of English-to-Albanian UI strings for common navigation, action, device, folder, and status labels.

## APIs, types, and data shape
The file is a flat JSON object used as a data module by Angular Translate. It exports no functions, classes, or runtime types. The parsed catalog has 69 keys against the 558-key English base, about 12.4% coverage. It has no extra keys, no empty values, and no interpolation-token mismatches; the only value equal to its English key is `LDAP`, which is expected for an acronym.

## Control flow
If the Albanian locale is made available, `$translate.use('sq')` would load this table and translate only the keys present here. Angular templates and controller calls continue to request English message IDs as lookup keys. Any missing Albanian entry falls back to the translation library behavior.

## State and persistence behavior
This catalog is immutable client-side data. It does not modify application settings or persisted configuration. Locale choice persistence is handled outside the file by `LocaleService` using the `SYN_LANG` localStorage key.

## Dependencies and integration points
The catalog depends on English message IDs from `lang-en.json`, Angular Translate, and Syncthing's generated language asset pipeline. `valid-langs.js` does not list `sq`, so the file may exist in the tree without being offered by the default GUI language selector unless the language list is regenerated elsewhere.

## Risks
Coverage is very sparse: 489 base keys are missing, so most GUI screens would remain in fallback English. Because the file has no interpolation examples, future additions with placeholders need explicit placeholder parity checks. Direct edits are risky because the directory README says Weblate is the authoritative source.

## Test signals
Run JSON parse validation, compare keys against `lang-en.json`, and confirm whether `sq` appears in generated available locales. If enabled manually, smoke-test basic navigation and verify fallback behavior is acceptable on screens with missing strings.
