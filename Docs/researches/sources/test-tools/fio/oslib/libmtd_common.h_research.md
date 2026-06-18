# sources/test-tools/fio/oslib/libmtd_common.h

Purpose: shared support macros and helpers for imported MTD utility code.

Important APIs/types: requires `PROGRAM_NAME`; defines `MIN`, `MAX`, `ALIGN`, typed min/max GNU statement expressions, `O_CLOEXEC` fallback, `PRIxoff_t`/`PRIdoff_t`, logging macros (`normsg`, `errmsg`, `sys_errmsg`, `warnmsg`), `is_power_of_2()`, `simple_strtoX()` conversion wrappers, and `common_print_version()`. It includes `libmtd_xalloc.h`.

Control flow and state: mostly macros; error macros print to `stderr` and return `-1`, while `*_die` variants exit. `simple_strtoX` inline helpers set an error flag if conversion leaves trailing text.

Dependencies and integration: used by `libmtd.c` and `libmtd_legacy.c`; assumes GNU C extensions (`__typeof__`, statement expressions) and libc feature macros.

Risks: macros evaluate arguments carefully in some places but still expose global names like `min`. Error handling prints directly rather than integrating with fio's normal logging. The required `PROGRAM_NAME` macro must be set before inclusion.

Test signals: build with compilers supporting GNU extensions; exercise parse and logging paths in MTD tests.
