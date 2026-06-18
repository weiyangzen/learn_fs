<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat.c -->
# sources/test-tools/strace/src/xlat.c

Purpose: Runtime implementation of xlat lookup and printing, including table search, reverse lookup, eq-or-less lookup, raw/abbrev/verbose formatting, and flag decomposition.

Important APIs/types/functions:
- Helper functions include `get_xlat_style`, `sprint_xlat_val`, `print_xlat_val`, `tprints_xlat_const`, `xlat_bsearch_compare`, `xlookup`, `xrlookup`, `xlat_search_eq_or_less`, `xlookup_le`, `printxvals_ex`, `sprintxval_ex`, `sprintflags_ex`, `printflags_ex`, `print_xlat_ex`
- Direct includes: `"defs.h"`, `"color.h"`, `"xstring.h"`, `<stdarg.h>`

Control flow:
- dispatches switch cases such as `XLAT_STYLE_FMT_D`, `XLAT_STYLE_FMT_U`, `XLAT_STYLE_FMT_X`, `XT_NORMAL`, `XT_SORTED`, `XT_INDEXED`, `XT_SORTED`, `XT_NORMAL`, `XT_INDEXED`, `XLAT_STYLE_ABBREV`, `XLAT_STYLE_RAW`, `XLAT_STYLE_VERBOSE`

State and persistence behavior:
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover raw, abbrev, and verbose xlat styles
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat.c -->
