# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/cputime.c

Read fully: 30 lines, 336 bytes. SHA-256 prefix: `d89655368e1a7bc8`.

This is a small Unix compatibility file for the linker. `cputime()` calls `times()`, sums user/system child and process slots, and returns hundredths as seconds. `seek()` wraps `lseek()`. `create()` wraps `creat()` but only accepts mode `1`, returning `-1` otherwise.

Integration: used by verbose timing logs in the linker pipeline and by `obj.c`/`asm.c` output creation and seeking. The wrappers preserve Plan 9-style names expected elsewhere in the code.

Risk notes: `create()` is intentionally narrow and does not emulate all Plan 9 open modes.
