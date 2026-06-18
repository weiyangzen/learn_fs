# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/sys.h

- Role: System-dependent declarations and common includes for upas.
- Key content: Plan 9 headers, `String.h`, `Mlock`, config globals, and prototypes for all `libsys.c` wrappers plus identity/path helpers.
- Integration: Included by `common.h`.
- Risks/notes: Declares `void exit(int)` to map C-style exit calls to Plan 9 `exits`, which can conflict with standard C expectations in other contexts.
