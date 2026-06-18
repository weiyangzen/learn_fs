# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/strncat_naive.S

This ARM assembly routine implements `strncat` in a simple byte loop. It first scans to the destination NUL terminator, then copies up to `n` bytes from the source, stops on source NUL or count exhaustion, writes a terminating NUL, and returns the original destination pointer.
