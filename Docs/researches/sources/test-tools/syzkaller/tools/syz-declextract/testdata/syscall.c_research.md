# sources/test-tools/syzkaller/tools/syz-declextract/testdata/syscall.c

Purpose: this fixture tests basic syscall extraction from macro-expanded definitions and pointer/string argument typing.

Important APIs and flow: includes `syscall.h` and defines `SYSCALL_DEFINE1(open, const char* filename, int flags, int mode)` and `SYSCALL_DEFINE1(chmod, const char* filename, int mode)`, each returning zero.

State and persistence: none.

Dependencies and integration: macro expansion creates `__do_sys_open` and `__do_sys_chmod` for JSON syscall records.

Risks: it uses `SYSCALL_DEFINE1` despite multiple variadic arguments because the fixture macro ignores the count parameter; this is intentional but not a faithful kernel macro.

Test signals: paired JSON should expose both syscalls, const string pointers for filename args, and integer mode/flags args.
