# sources/user-network-fs/samba/source4/torture/torture.c

## Purpose
`torture.c` provides the small core registration layer for smbtorture modules. It owns global default torture settings, the root suite pointer, suite registration, and module initialization for static and shared smbtorture modules.

## Important APIs, Types, and Functions
The file defines `_PUBLIC_` globals `torture_numops`, `torture_entries`, `torture_failures`, `torture_seed`, and `torture_numasync`, plus `struct torture_suite *torture_root`. Public functions are `torture_register_suite()` and `torture_init()`.

## Control Flow
`torture_register_suite()` treats a NULL suite as success, lazily allocates `torture_root` with `talloc_zero()`, and adds the provided suite under the root with `torture_suite_add_suite()`. `torture_init()` expands static module prototypes, builds a static init array from `STATIC_smbtorture_MODULES`, loads shared modules named `smbtorture`, runs both static and shared init functions, frees the shared init array, and returns success.

## State and Persistence Behavior
The file creates process-lifetime test registry state in `torture_root` and stores default numeric settings used by many tests. Module initialization mutates this registry by calling each module's init function.

## Dependencies and Integration Points
It depends on the generic torture harness, Samba module loading, talloc, and generated static module macros. `smbtorture.c` calls `torture_init()`, while each suite module calls `torture_register_suite()`.

## Risks
If `torture_root` allocation fails, `torture_suite_add_suite()` receives NULL root state. Module init failures are not surfaced in the return value because `run_init_functions()` results are not checked here. Global defaults are shared across all tests in a process.

## Test Signals
Indirect signals include visible suites after initialization, successful module loading, and `smbtorture --list-suites` showing registered modules.
