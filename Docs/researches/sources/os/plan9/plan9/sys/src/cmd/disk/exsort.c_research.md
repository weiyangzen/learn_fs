# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/exsort.c

Standalone utility for inspecting and optionally rewriting `/adm/cache`-style arrays of 32-bit block numbers.

It reads the whole file as `ulong` values, counts how many values have bit 7 and bit 31 set, and if high-bit count exceeds low-bit count treats the data as byte-swapped and swaps every word. It sorts values numerically, then reports counts per disk-sized range using `Wormsize = 157933` for disk numbers 0 through 99 and a total.

With `-w`, it opens the file read/write and writes the sorted values back, swapping back first if it originally detected swapped byte order. Without `-w`, it is read-only. Default file is `/adm/cache`.

Risks and notes: reads entire file into memory, assumes file length is a multiple of `sizeof(long)`, and uses a heuristic for byte order. It prints `cant` style errors and exits with simple status strings.
