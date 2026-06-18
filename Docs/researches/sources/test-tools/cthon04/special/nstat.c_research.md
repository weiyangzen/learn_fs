# sources/test-tools/cthon04/special/nstat.c

## Purpose
times repeated `stat()` calls against the program path to measure metadata lookup/cache behavior.

## Important APIs, Types, and Functions
`main()` uses `starttime()`, `endtime()`, `struct timeval`, `struct stat`, and a `stats` counter.

## Control Flow and State
It parses a count, loops `stat(argv[0])`, increments counters, computes elapsed seconds, and prints calls/sec plus msec/call.

## Persistence and Dependencies
no persistent filesystem changes. Dependencies: `../basic/subr.o` timing helpers through `../tests.h` plus `stat` headers.

## Integration Points, Risks, and Test Signals
Integration is metadata-rate testing. Risks are statting the executable instead of an arbitrary target and division-by-zero guard only for exact zero elapsed. Signals are successful timing output.
