# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtodt.c

Data-file validator for libc/gdtoa `strtod`.

Input format: triples containing decimal string plus expected high/low hex words. It can read stdin or named files.

Behavior:
- Determines host double word order at runtime using `1.0`.
- For each non-comment line, parses expected words with `strtoul`.
- Converts the decimal prefix with `strtod`.
- Reports bit mismatches and returns nonzero if any bad conversions occurred.
- `-?` prints usage.

Dependencies: `gdtoa.h` for `ULong`, libc `strtod`.
