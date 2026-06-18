# File Research: sources/os/plan9/9front/sys/src/cmd/syscall/syscall.c

`syscall.c` is a diagnostic command for invoking named system calls directly from the command line.

Key pieces:
- Defines a 1 MiB global `buf` and up to five parsed uintptr arguments.
- Declares syscall wrappers not exposed by libc headers.
- Includes generated `tab.h`, built from `mktab.awk`, mapping names to function pointers.
- `parse` maps arguments beginning with `buf` to the global buffer, parses numeric constants with `strtoull`, or otherwise passes the string pointer.
- `main` locates the syscall name, installs a note handler, calls the function, and reports return value/error.

Options:
- `-o` writes `buf` to stdout after the syscall, using the return value as byte count except for `_ERRSTR`, `ERRSTR`, and `FD2PATH`, where it uses `strlen(buf)`.
- `-s` decodes `buf` as a stat message with `convM2D` and prints `%D`.

Special handling:
- `seek`, `pread`, and `pwrite` use `strtoll` for vlong offset arguments because the generic uintptr path cannot safely represent those call signatures.

Risks:
- Intentionally unsafe: arbitrary syscalls with arbitrary pointers/integers can crash or mutate process/kernel-visible state.
- Buffer output count uses syscall return value and can be invalid if the invoked call does not return a byte count.
