# sources/test-tools/strace/src/stat64.c

Purpose: decodes 64-bit stat-family syscalls using the common `strace_stat` representation.

Important APIs/types/functions: `decode_struct_stat64`, `SYS_FUNC(stat64)`, `SYS_FUNC(fstat64)`, `SYS_FUNC(fstatat64)`, `fetch_struct_stat64`, and `print_struct_stat`.

Control flow: mirrors `stat.c`: entry prints path/fd/dirfd inputs; exit fetches and prints stat64 output buffer; `fstatat64` prints `AT_*` flags.

State and persistence behavior: stateless stack-local decode.

Dependencies and integration points: depends on `fetch_struct_stat64`, `stat.h`, path/fd helpers, and syscall table mappings for older 32-bit ABIs exposing `stat64`.

Risks: easy to confuse with `stat.c`; fetch helper selection is the main correctness boundary. 64-bit fields must remain normalized without truncation.

Test signals: stat64/fstat64/fstatat64 on 32-bit personalities, large files/inodes, invalid output buffers, and flags output.
