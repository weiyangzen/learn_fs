# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/et_h.awk

## Purpose
`et_h.awk` generates the C header for an `.et` error table.

## Important APIs, Types, and Functions
It emits `#include <et/com_err.h>`, `#define` constants for each error code, `extern` declarations for the generated table and initializer functions, `ERROR_TABLE_BASE_<table>`, and old-name compatibility macros.

## Control Flow
The script computes the same table base as `et_c.awk`, tracks prefixes and explicit indexes, and emits each error-code macro with increasing values. The `END` block writes declarations and compatibility aliases.

## State, Persistence, Dependencies, Risks, and Test Signals
State is AWK arithmetic for current code value and table base. Dependencies are AWK, `com_err.h`, and matching generated source. Risks include duplicated base logic diverging from `et_c.awk`, the same negative carry typo pattern, and limited grammar tolerance. Test signals are exact header diffs in the lib/et check target.
