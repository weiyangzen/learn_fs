# sources/test-tools/strace/src/stat.c

Purpose: decodes legacy/non-64-bit `stat`, `fstat`, and `newfstatat` syscalls into the common `strace_stat` printer.

Important APIs/types/functions: `decode_struct_stat`, `SYS_FUNC(stat)`, `SYS_FUNC(fstat)`, `SYS_FUNC(newfstatat)`, `fetch_struct_stat`, `print_struct_stat`, `printpath`, `printfd`, `print_dirfd`, and `at_flags`.

Control flow: entry prints path, fd, or dirfd/path inputs. Exit fetches the output stat buffer and prints it through the normalized common stat representation; `newfstatat` then prints flags.

State and persistence behavior: stateless stack-local normalized stat data.

Dependencies and integration points: relies on architecture/personality-specific `fetch_struct_stat` and shared `stat.h` internal representation. Integrates with path/fd printing and AT flag xlats.

Risks: all ABI complexity is in fetch helpers; this wrapper must call the correct fetch function for non-64-bit stat layout. Flags are output on exit, so failed syscalls still show path inputs but may not decode a stat buffer.

Test signals: stat/fstat/newfstatat success and failure, invalid statbuf, symlink/no-follow flags, and personality-specific stat layout.
