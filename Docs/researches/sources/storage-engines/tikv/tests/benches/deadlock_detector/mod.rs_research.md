# sources/storage-engines/tikv/tests/benches/deadlock_detector/mod.rs

## Purpose
This Criterion benchmark measures TiKV deadlock detector table performance under dense wait-for graph insertion patterns with and without cleanup pressure.

## Important APIs, Types, and Functions
`DetectGenerator` produces `WaitForEntry` records with monotonically increasing transaction ids and random wait-for transactions/key hashes in a configurable range. `Config` carries request count per iteration, transaction range, and TTL. `bench_detect` feeds generated entries into `DetectTable::detect`.

## Control Flow
Two benchmark groups are registered. `bench_dense_detect_without_cleanup` varies wait-for range with huge TTL to reduce cleanup. `bench_dense_detect_with_cleanup` varies TTL at fixed range to exercise expiration/cleanup costs. `main` uses Criterion sample size 10.

## State and Persistence Behavior
State is an in-memory `DetectTable` per bench function and generator state. No durable storage is used.

## Dependencies and Integration Points
It depends on `kvproto::deadlock`, TiKV lock-manager `DetectTable`, Criterion, random generation, and TiKV duration utilities.

## Risks and Test Signals
Randomness can introduce noise, while dense ranges can produce different cycle/collision behavior. Useful signals are per-range and per-TTL performance trends plus compilation against deadlock detector API changes.
