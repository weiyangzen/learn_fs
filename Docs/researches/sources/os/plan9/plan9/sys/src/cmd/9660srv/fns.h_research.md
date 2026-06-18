# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/fns.h

Purpose: shared 9660srv function declarations and error-stack macros.

Key behavior: declares logging, allocation, buffer, device, fid, reference, and stat helper functions. Defines `waserror()` and `poperror()` around the global jump-buffer stack.

Integration notes: used by all 9660srv C files. Error handling is non-local via `longjmp`; callers must balance `waserror`/`poperror`.
