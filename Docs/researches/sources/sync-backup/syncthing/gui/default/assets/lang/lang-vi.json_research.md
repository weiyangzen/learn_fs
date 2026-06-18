# sources/sync-backup/syncthing/gui/default/assets/lang/lang-vi.json

## Purpose
`lang-vi.json` is the Vietnamese translation catalog for the Syncthing default web GUI. It covers about half of the current English catalog, with translations for many common device/folder actions, warnings, ignore patterns, file versioning concepts, and synchronization status labels.

## APIs, types, and data shape
The file is a flat JSON object and has no executable exports. The parsed catalog has 276 keys against the 558-key English base, about 49.5% coverage. It has no extra keys and no placeholder-token mismatches. Two values are empty strings, and two values match English exactly (`LDAP` and `OK`).

## Control flow
If Vietnamese is selected, Angular Translate looks up English message IDs in this table for directives, filters, and controller-generated labels. Present placeholder-bearing strings preserve the expected interpolation token names, so dynamic values such as device IDs, folder labels, paths, versions, and URLs can be inserted safely. Missing or empty entries rely on translation fallback behavior or may render as blank depending on Angular Translate handling for the exact path.

## State and persistence behavior
This file is static localization data. It does not persist settings, sync state, or user choices. The selected locale is managed separately by `LocaleService`, including localStorage persistence under `SYN_LANG`.

## Dependencies and integration points
The catalog depends on Angular Translate and the English base key set. `valid-langs.js` does not include `vi`, so this file is not currently exposed in the default checked-in language selector. The directory README indicates the file is generated from Weblate rather than manually maintained.

## Risks
Coverage is partial, with 282 missing English keys across automatic-upgrade copy, block indexing, cleanup/versioning controls, connection management, copy helpers, database/configuration paths, debug labels, and many newer status strings. The two empty translations are higher risk than missing keys because they may produce blank UI text. Not being listed in `valid-langs.js` creates a visible-integration risk.

## Test signals
Run JSON parse validation, key coverage diff, placeholder parity, and an explicit empty-value check. If enabling Vietnamese in the language list, first resolve empty entries and smoke-test settings, folder/device editing, notifications, logs, and version restore flows for fallback or blank labels.
