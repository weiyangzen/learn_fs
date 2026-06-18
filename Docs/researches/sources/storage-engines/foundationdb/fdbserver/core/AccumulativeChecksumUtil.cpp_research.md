# sources/storage-engines/foundationdb/fdbserver/core/AccumulativeChecksumUtil.cpp

## Purpose
Implements helper logic for mutation checksums and accumulative checksum tracking. Commit-side builders assign checksum metadata and maintain per-tag checksum state; storage-side validators buffer mutations and verify emitted accumulative checksum mutations.

## Important APIs, Types, and Functions
- `updateMutationWithAcsAndAddMutationToAcsBuilder()` overloads populate mutation checksums, set the ACS index, and add the mutation for one tag, a vector of tags, or a set of tags.
- `AccumulativeChecksumBuilder::addMutation()`, `updateTable()`, and `newTag()` update per-tag ACS state and reset state when a tag is newly assigned.
- `AccumulativeChecksumValidator::addMutation()` buffers mutations for a version and index.
- `processAccumulativeChecksum()` compares buffered aggregate checksum state with the ACS mutation, updates the validator table, and clears the buffer.
- `restore()` seeds validator state from persisted ACS state, while getter methods return and reset counters.

## Control Flow
Commit-side flow calculates a mutation checksum, stamps its ACS index, and folds the mutation checksum into `acsTable` by tag. Storage-side flow buffers mutations until an ACS mutation arrives, checks all buffered mutations share the expected version/index, aggregates them from the previous stored checksum, compares against the ACS mutation, then advances table state.

## State and Persistence Behavior
Builder state is in-memory per tag, keyed by `Tag`, and records ACS value, version, epoch, and index. Validator state is in-memory per ACS index, can be restored from persisted `AccumulativeChecksumState`, and treats a higher epoch as a reset of older state. Corruption paths throw `please_reboot()` after `SevError` trace events.

## Dependencies and Integration Points
Depends on `AccumulativeChecksumUtil.h`, mutation serialization/checksum support, log epochs, tags, protocol versions, and `CLIENT_KNOBS` feature gates. It integrates with commit proxy mutation generation and storage server mutation validation.

## Risks and Edge Cases
All main paths assert both mutation checksum and ACS knobs are enabled. Version ordering is asserted in the builder. Validator correctness depends on ACS mutations arriving after all mutations for that version/index; stale buffers are logged by `clearCache()`. New epochs deliberately discard old table state.

## Test Signals
Embedded `noSim/AccumulativeChecksum/MutationRef` verifies mutation encoding/decoding, checksum validation, ACS index serialization, and ACS mutation serialization. Broader corruption detection requires simulation or storage-server tests with ACS enabled.
