# sources/test-tools/strace/src/hostname.c

Decoders for hostname syscalls. `sethostname` prints the input buffer with the supplied length; `gethostname` prints the output buffer on successful exit or address on failure plus size. State is syscall phase and tracee string memory. Dependencies are string printers and `<linux/utsname.h>` where needed. Risks are non-NUL buffers, length truncation, output after failure, and libc/kernel semantic differences. Tests should cover set/get, too-small buffers, non-NUL data, bad pointers, and zero sizes.
