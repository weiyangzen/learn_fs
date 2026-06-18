# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/memory_.h

`memory_.h` is Ghostscript's portable wrapper for memory and string-copy functions. It includes `std.h` first, then chooses the right system declarations or substitutes based on compiler/platform macros.

For Turbo C it uses `<mem.h>` and an inline `memcmp` path. For modern POSIX/STDC/VMS/HPUX/Watcom/Think C/BSDI/FreeBSD/MSVC cases it uses `<string.h>`. Older BSD/UTEK paths map `memcpy` to `bcopy`, `memcmp` to `bcmp`, declare `bcopy/bcmp/bzero`, and request Ghostscript replacements for missing functions. Some System V/Sun paths request a replacement `memmove`.

Under `PROFILE`, it forces Ghostscript replacements for `memset`, `memcpy`, and `memmove`. Requested substitutions are declared as `gs_memmove`, `gs_memcpy`, `gs_memset`, and `gs_memchr`, with macros redirecting standard names. The risk is compatibility complexity and subtle differences such as old `bcmp` return values.
