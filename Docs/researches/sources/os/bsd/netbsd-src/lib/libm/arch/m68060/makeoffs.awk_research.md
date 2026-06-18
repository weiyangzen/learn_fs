# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/makeoffs.awk

AWK converter for FPLSP data. It tracks 16-byte offset slots for `.long` records and emits `ENTRY_NOPROFILE(__fplsp060_XXXX)` labels for offsets in the first 1024 bytes.
