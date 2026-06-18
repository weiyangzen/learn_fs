# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/syscall.h

Purpose: this fixture header provides minimal syscall-definition macros that expand synthetic `SYSCALL_DEFINE*` declarations into `__do_sys_<name>` functions.

Important APIs and flow: `SYSCALL_DEFINE1` and `SYSCALL_DEFINE2` forward to `SYSCALL_DEFINEx`, which emits a prototype and definition for `long __do_sys_NAME(__VA_ARGS__)`.

State and persistence: preprocessor-only definitions; no state.

Dependencies and integration: included by syscall-oriented declextract fixtures such as `cover.c`, `functions.c`, `scopes.c`, `syscall.c`, and `types.c`. It lets clang extraction see stable function names matching kernel syscall implementation naming.

Risks: the macro ignores true Linux syscall wrapper complexity, calling conventions, and metadata sections. It is intentionally small for deterministic tests.

Test signals: golden JSON should map syscalls to `__do_sys_*` functions with extracted argument types.
