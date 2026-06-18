<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/utimes.c -->
# sources/test-tools/strace/src/utimes.c

Purpose: Decoder family for `utimes`, `futimesat`, and `utimensat` time32/time64 variants, including dirfd/path/timestamp pairs and `AT_*` flags.

Important APIs/types/functions:
- SYS_FUNC handlers: `utimes`, `futimesat`, `utimensat_time32`, `utimensat_time64`, `osf_utimes`
- Helper functions include `do_utimensat`
- Direct includes: `"defs.h"`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- main risk is semantic drift when syscall ABI or generated xlat definitions change

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/utimes.c -->
