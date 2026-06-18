# sources/security-integrity/gocryptfs/tests/reverse/longname_perf_test.go

## Purpose
Benchmark for reverse-mode stat performance over very large numbers of long-name files.

## Important APIs, Types, And Functions
- `genName` formats numbered long filenames using the shared `x240` suffix.
- `generateLongnameFiles` creates 100000 long-name files.
- `BenchmarkLongnameStat` enumerates encrypted names in `dirB` and repeatedly stats them.

## Control Flow
The benchmark seeds `dirA` with long files, reads the encrypted directory listing once, resets the timer, and stats encrypted names round-robin for `b.N` iterations.

## State And Persistence
It creates a large persistent set of files during benchmark setup and removes/recreates `dirA` after timing stops.

## Dependencies And Integration Points
Depends on the reverse `TestMain` mount, `x240`, and filesystem ability to handle 100000 entries.

## Risks And Edge Cases
The comment says 10000 files but the loop creates 100000. It is expensive and can dominate benchmark setup time or temp storage.

## Test Signals
Signal is benchmark latency for stat calls in the encrypted reverse view without stat failures.
