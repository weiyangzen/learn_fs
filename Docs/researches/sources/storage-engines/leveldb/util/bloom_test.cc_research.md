# sources/storage-engines/leveldb/util/bloom_test.cc

## Purpose
`bloom_test.cc` validates the built-in Bloom filter policy.

## Important APIs, Types, and Functions
`BloomTest` owns a `FilterPolicy`, buffers pending keys, builds filters, checks matches, estimates false-positive rate, and can dump bit patterns. Helper `Key` encodes integers as fixed32 slices.

## Control Flow
Tests cover empty filters, small filters, and a sweep from 1 to 10,000 keys. For each size the test builds a filter, verifies all inserted keys match, probes 10,000 distant keys, enforces size bounds, and bounds false positives below 2% with few mediocre cases.

## State, Dependencies, and Integration
It depends on `filter_policy`, `coding`, `logging`, and test utilities. It is a statistical guard for filter quality and encoding stability.

## Risks and Test Signals
False positives are allowed but bounded; false negatives fail immediately. The test is deterministic because key generation and probe ranges are fixed.
