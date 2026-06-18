# sources/storage-engines/tikv/components/raftstore/src/coprocessor/consistency_check.rs

## Purpose
This file defines the raftstore coprocessor consistency-check observer interface and a raw-data implementation that computes CRC32 over all key/value pairs in a region plus the region state record. It supports consistency verification across replicas.

## Important APIs, Types, and Functions
- `ConsistencyCheckObserver<E>` extends `Coprocessor` with `update_context()` and `compute_hash()`. Observers append policy markers to a context and later compute hashes from snapshots.
- `Raw<E>` is a zero-sized observer using `PhantomData<E>`.
- `Raw::update_context()` appends `ConsistencyCheckMethod::Raw` to the context and returns `true`, indicating later observers should be skipped because raw checking is strongest/heaviest.
- `Raw::compute_hash()` consumes the raw-method marker from context and delegates to `compute_hash_on_raw()`.
- `compute_hash_on_raw()` scans all snapshot CFs over encoded region bounds, feeds keys and values into `crc32fast::Hasher`, then includes the `CF_RAFT` region-state key and value if present.

## Control Flow
During context construction, observers can append method identifiers and stop further observers. During hash computation, `Raw` checks that context is nonempty, asserts the first byte is the raw method marker, advances the context slice, and computes the digest from snapshot data and region state.

## State and Persistence Behavior
This file is read-only against snapshots. It does not persist data, but it includes persistent region-local state in the hash so metadata divergence is detected along with user data divergence.

## Dependencies and Integration Points
It depends on `engine_traits::{KvEngine, Snapshot, CF_RAFT}`, `kvproto::metapb::Region`, raftstore coprocessor traits, consistency-check config enum, `keys` region/data key encoding, and `crc32fast`.

## Risks and Edge Cases
- `compute_hash()` asserts the context marker; malformed context can panic rather than return an error.
- Raw consistency scan is heavy because it scans every CF over the full encoded region range.
- Snapshot `cf_names()` controls which CFs participate; engine implementations must expose the expected CF set.
- Region state inclusion reads from `CF_RAFT`, so missing region state is tolerated but divergent present values alter the hash.

## Test Signals
The in-file `test_update_context()` verifies that raw observer appends exactly one context byte with the raw method value and requests observer skipping.
