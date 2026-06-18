# sources/storage-engines/rocksdb/db/db_iter_stress_test.cc

## Purpose

This file is a randomized differential stress test for `DBIter`. It builds a synthetic ordered internal-key dataset, wraps it in an `InternalIterator` that can fail or mutate visibility during operations, and compares `DBIter` behavior with a simpler reference iterator. The goal is to catch iterator state-machine bugs around forward/reverse movement, seek positioning, merges, deletions, invisible versions, status propagation, and data changing under the iterator.

## Important APIs, types, and functions

`Entry` represents an internal record with user key, `ValueType`, sequence number, encoded internal key, value, and a `visible` flag used to simulate entries appearing/disappearing. Its ordering sorts by user key ascending and sequence/type descending, matching RocksDB internal-key order.

`Data` owns the vector of entries, indexes of hidden entries, and a set of keys whose visibility changed since the last seek. Recently touched keys are excluded from exact reference comparison because the underlying iterator is allowed to mutate during a single DBIter operation.

`StressTestIterator` implements `InternalIterator`. It supports `SeekToFirst`, `SeekToLast`, `Seek`, `SeekForPrev`, `Next`, `Prev`, `key`, `value`, `status`, and pinning checks. `MaybeFail()` injects `Incomplete` or `IOError` according to probability. `MaybeMutate()` randomly hides or unhides entries to simulate compaction-like disappearance or reappearance. `SkipForward` and `SkipBackward` advance over hidden entries.

`ReferenceIterator` is a compact model of visible DB iteration. It scans the sorted `Data` with binary search, ignores recently touched keys, applies snapshot sequence filtering, handles `kTypeDeletion`, `kTypeValue`, and `kTypeMerge`, and implements stringappend-style merge by concatenating operands/base values from oldest to newest reference order.

## Control flow

The single `StressTest` uses a deterministic `Random64` seed. It iterates over combinations of entry count, key-space density, prevalent entry type, error probability, mutation probability, and target hidden fraction. For each combination it creates sorted internal entries with random keys, sequence numbers equal to insertion index, mostly one prevalent type plus occasional other types, and encoded internal keys via `AppendInternalKey`.

During each run, a new `DBIter` and `ReferenceIterator` are created about every 30 operations at a random snapshot sequence. The DBIter wraps a fresh `StressTestIterator` and is constructed through `DBIter::NewIter` with a stringappend merge operator. Each iteration randomly chooses forward or reverse movement. It performs `Next`/`Prev` most of the time when valid, and otherwise or occasionally performs `Seek`, `SeekForPrev`, `SeekToFirst`, or `SeekToLast`.

After each operation, the test compares outcomes. If DBIter is valid and the key was not recently touched, key and value must exactly match the reference iterator. If the DBIter lands on a recently mutated key, the test checks only monotonic movement and that DBIter did not skip a stable reference key. If DBIter is invalid with OK status, the reference must also be invalid. If DBIter has non-OK status, the next reference operation is forced to reseek because exact position is no longer meaningful.

## State and persistence behavior

The test has no durable storage; all state is in memory. It nevertheless models key RocksDB iterator conditions: hidden entries stand in for records removed or obscured by compaction, random failures stand in for underlying storage errors, and repeated reconstruction of iterators models new snapshots. The deterministic seed makes failures reproducible. `StressTestIterator` advertises pinned keys and values, which is important because DBIter reverse paths require pinned value support in some cases.

## Dependencies and integration points

The test includes `db/db_iter.h`, `db/dbformat.h`, RocksDB comparator/options/slice headers, the test harness, random/string utilities, and `utilities/merge_operators.h`. It directly constructs `ImmutableOptions` and `MutableCFOptions` from `Options`, uses `BytewiseComparator`, and passes `version=nullptr`, no read callback, and no active memtable, isolating the core DBIter state machine from actual DB storage.

Command-line integration is optional through gflags. With `FLAGS_verbose`, the test prints generated entries, operations, injected errors, and mutations, which helps reproduce a failing trace.

## Risks and edge cases

The reference model intentionally implements only part of full DBIter behavior: no timestamps, prefix extractors, bounds, blob indexes, wide columns, range tombstone conversion, unprepared values, or read callbacks. The file's TODO notes these coverage gaps and also suggests testing pinning more aggressively. Because mutations happen inside underlying iterator operations, exact comparison is impossible for recently touched keys; the test uses directional and non-skip assertions instead. High mutation and error probabilities increase coverage but can make a failure trace long, hence the verbose debug flag.

## Test signals

At the end, the test requires more than 10,000 exact matches, end-reached cases, non-OK statuses, and recently-mutated-key cases. These counters verify that the randomized matrix exercised all major result classes. The strongest signal is differential agreement between DBIter and `ReferenceIterator` across random direction changes, seeks, deletions, merges, invisible entries, errors, and mutations.
