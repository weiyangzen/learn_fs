# sources/test-tools/syzkaller/tools/syz-declextract/testdata/cover.c.json

Purpose: this golden clang extraction output describes the `cover.c` fixture for downstream declextract tests.

Important structure: top-level keys are `functions`, `consts`, and `syscalls`. Functions include `__do_sys_cover` and static `cover_helper`. Constants define `COVER_IOCTL1` through `COVER_IOCTL4` with numeric values 1 through 4. The syscall record maps `__do_sys_cover` to one integer `cmd` argument.

Control-flow and facts: `__do_sys_cover` has an arg-independent return fact from local `tmp`, separate scopes for `COVER_IOCTL1`, `COVER_IOCTL2`, and combined `COVER_IOCTL3`/`COVER_IOCTL4`; the combined scope calls `cover_helper` and records argument 0 flowing to helper argument 0. `cover_helper` has separate scopes for constants 3 and 4.

State and persistence: this is static JSON consumed through the clangtool cache symlink in tests. It must remain in sync with source line numbers and fixture constants.

Risks and test signals: schema drift or source line changes break golden tests. It specifically tests switch grouping, helper-call propagation, syscall argument typing, and constant extraction.
