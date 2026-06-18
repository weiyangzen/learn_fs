# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/makefile

Test makefile for building and running the gdtoa validation programs.

Important targets:
- Builds `dt`, `dItest`, `ddtest`, `dtest`, `ftest`, `Qtest`, `xtest`, `xLtest`, sudden-underflow variants, `strtodt`, `strtodtnrp`, and `pftest`.
- `Q.out x.out xL.out` uses `xQtest` to select expected output files based on `sizeof(long double)`.
- `tests` compares generated outputs against checked-in `.out` files, collecting mismatches in `bad`.
- Notes that Intel-like extended precision may cause `strtodt` double-rounding surprises, while `strtodtnrp` should not.

Build details:
- Uses `-I..` and architecture gdtoa include directory.
- Uses `INFFIX` sed normalization for infinity spelling.
- `xsum.out` verifies the test corpus checksum.
