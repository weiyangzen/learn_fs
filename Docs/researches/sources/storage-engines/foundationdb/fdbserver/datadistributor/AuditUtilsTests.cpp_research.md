# `sources/storage-engines/foundationdb/fdbserver/datadistributor/AuditUtilsTests.cpp`

## Purpose

This file is a Flow unit-test translation unit for audit helper routines declared in `fdbclient/AuditUtils.h`. It verifies range-list normalization and bidirectional consistency checks between the KeyServers view and ServerKeys view of shard ownership. `forceLinkAuditUtilsTests()` exists only to keep the tests linked into the datadistributor test target.

## Important APIs and Test Cases

- `coalesceRangeList()` is tested for empty input, a single unchanged range, sorting of non-overlapping ranges, overlap merging, adjacency merging, and containment absorption.
- `rangesSame()` is tested for empty equivalence, empty-vs-non-empty mismatch, exact equality, equivalent coverage with different split points, mismatched begin/end boundaries, and gaps.
- `checkLocationMetadataConsistency()` is tested with per-server maps keyed by `UID`, exercising consistent ownership, missing ServerKeys entries, missing KeyServers entries, per-server range mismatches, multiple simultaneous errors, and both maps empty.
- `buildLocationMetadataMaps()` is tested as the production preparation path before calling `checkLocationMetadataConsistency()`, including missing ownership, phantom server ownership, shifted boundaries, and partial ownership.

## Control Flow

The file uses independent `TEST_CASE` blocks. Each block constructs `UID`s and `KeyRange`s, builds small `std::unordered_map<UID, std::vector<KeyRange>>` fixtures, calls one audit helper, and asserts either an empty result or specific error content. The production-path tests call `buildLocationMetadataMaps()` first, then pass `builtMaps.fromKeyServers` and `builtMaps.fromServerKeys` into the consistency checker.

## State and Persistence Behavior

The tests are pure in-memory checks. They do not create transactions, use actors, or write system keys. The only state is local vectors/maps and returned `LocationMetadataError` objects. Their persistence relevance is indirect: they validate logic used to compare durable KeyServers and ServerKeys metadata views elsewhere in the system.

## Dependencies and Integration Points

The file depends on `fdbclient/AuditUtils.h`, `fdbclient/FDBTypes.h`, and `flow/UnitTest.h`. It is compiled into the datadistributor unit-test target by the local CMake file. The tested helpers are also referenced by production data-distribution audit logic and storage-server ownership validation paths, so these tests guard common range-comparison semantics rather than datadistributor-only code.

## Risks and Edge Cases

The assertions check message substrings, which confirms error category but not the full diagnostic payload. The fixtures use simple printable keys and do not cover system key boundaries, empty ranges inside non-empty maps, duplicated server entries beyond vector coalescing, or very fragmented range lists. Because the tests rely on exact error counts in multi-error scenarios, future helper changes that aggregate or de-duplicate errors could require test updates even if audit behavior remains acceptable.

## Test Signals

This file is itself test coverage. Strong signals include split-point-insensitive equality, adjacency merging, and simultaneous detection of missing and mismatched server ownership. Missing signals include randomized/fuzzed range-list inputs and coverage for `buildOwnRangesFromServerKeysResult()` or raw KeyServers parsing, which are adjacent helpers in `AuditUtils.h` but outside this file.
