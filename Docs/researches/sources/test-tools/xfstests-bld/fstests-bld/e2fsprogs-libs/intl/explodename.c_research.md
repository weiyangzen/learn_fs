<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/explodename.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/explodename.c

## Purpose
This file splits locale names into language, territory, codeset, normalized codeset, modifier, and CEN-specific components for catalog fallback generation.

## Important APIs, Types, and Functions
Exports are `_nl_find_language(name)` and `_nl_explode_name(name, language, modifier, territory, codeset, normalized_codeset, special, sponsor, revision)`. It returns a bitmask using flags from `loadinfo.h`, including `TERRITORY`, `XPG_CODESET`, `XPG_NORM_CODESET`, `XPG_MODIFIER`, `CEN_AUDIENCE`, `CEN_SPECIAL`, `CEN_SPONSOR`, and `CEN_REVISION`.

## Control Flow
`_nl_find_language` scans to the first locale separator. `_nl_explode_name` destructively inserts NUL terminators into the input string, first parsing XPG syntax (`language[_territory[.codeset]][@modifier]`) and then CEN syntax (`language[_territory][+audience][+special][,sponsor][_revision]`). It normalizes non-empty codesets and clears empty XPG components from the mask.

## State and Persistence
The input locale string is modified in place. A normalized codeset may be dynamically allocated and must be freed by the caller when the returned mask includes `XPG_NORM_CODESET`.

## Dependencies and Integration Points
It depends on `_nl_normalize_codeset` from `l10nflist.c` and the bit flags in `loadinfo.h`. `finddomain.c` uses it before creating catalog fallback lists.

## Risks
Callers must pass mutable storage, not a string literal. The parser is legacy and may not understand every modern locale naming convention. Incorrect mask bits change fallback search order and catalog file names.

## Test Signals
Use locale strings such as `de_DE.UTF-8`, `sr_RS@latin`, `en+audience+special,sponsor_revision`, aliases without language, empty components, and normalized codesets like `ISO-8859-1`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/explodename.c -->
