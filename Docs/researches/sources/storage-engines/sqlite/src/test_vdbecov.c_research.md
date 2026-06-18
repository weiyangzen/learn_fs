# sources/storage-engines/sqlite/src/test_vdbecov.c

## Purpose

`test_vdbecov.c` is test-only Tcl support for SQLite VDBE branch coverage instrumentation. When both `SQLITE_TEST` and `SQLITE_VDBE_COVERAGE` are enabled, it registers `vdbe_coverage` so Tcl tests can start coverage collection, run SQL, and report VDBE source lines and branch paths that were never exercised.

## Important APIs, Types, And Functions

- `aBranchArray[200000]` is a static byte array indexed by VDBE source line or instrumentation id.
- `test_vdbe_branch()` is the callback registered with `SQLITE_TESTCTRL_VDBE_COVERAGE`; it ORs branch bits into `aBranchArray[iSrc]`.
- `appendToList()` appends `{line path never-description}` triples to a Tcl result list.
- `test_vdbe_coverage()` implements `vdbe_coverage start|report|stop`.
- `Sqlitetestvdbecov_Init()` registers the Tcl command when instrumentation is compiled in.

## Control Flow

`vdbe_coverage start` zeroes the array and installs `test_vdbe_branch()` through `sqlite3_test_control()`. VDBE execution elsewhere calls that callback with a source id, branch bit, and branch type. `vdbe_coverage report` scans every nonzero byte in the array and emits missing path entries for branch bits that were not seen. `vdbe_coverage stop` unregisters the callback by passing null pointers to the same test-control opcode.

The reporting logic treats high-nibble type `4` as a three-way comparison and labels missing paths as `less than`, `equal`, or `greater-than`; other instrumented branches are labeled `falls through`, `taken`, or `NULL`.

## State And Persistence Behavior

All state is process-local and test-only. Coverage data lives in `aBranchArray` until the next `start`, process exit, or command stop. No SQLite database state is modified, but the global VDBE coverage callback affects all connections in the test process while active.

## Dependencies And Integration Points

The module depends on `sqlite3_test_control(SQLITE_TESTCTRL_VDBE_COVERAGE, ...)`, VDBE instrumentation sites that call the registered callback, Tcl object APIs, and `sqliteInt.h` token/type definitions. It integrates with SQLite's Tcl testfixture through `Sqlitetestvdbecov_Init()`.

## Risks And Edge Cases

- Source ids beyond `sizeof(aBranchArray)` are silently ignored, so instrumentation growth can hide uncovered paths unless the array remains large enough.
- Coverage state is global and not thread-local; concurrent tests could race or mix coverage observations.
- Branch bits are accumulated with OR only, so there is no execution count or ordering information.
- The `iType` callback parameter is unused; reporting infers labels from bits stored in the high nibble of the branch byte.
- The file compiles to a no-op initializer when coverage support is omitted, so tests must gate expectations on compile options.

## Test Signals

Tests should verify `start` resets old observations, SQL execution populates expected branch entries, `report` returns missing paths with stable line/path labels, and `stop` disables further accumulation. Build-matrix tests should verify the command exists only when `SQLITE_VDBE_COVERAGE` is defined.
