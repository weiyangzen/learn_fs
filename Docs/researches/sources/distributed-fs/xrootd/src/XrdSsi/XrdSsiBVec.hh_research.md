# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiBVec.hh

## Purpose
Defines a compact bit-vector helper optimized for small integer values while supporting arbitrary larger values through a set.

## Important APIs, Types, And Functions
- `Set(uint32_t bval)` records a value.
- `IsSet(uint32_t bval)` checks membership.
- `UnSet(uint32_t bval)` removes a value.
- `Reset()` clears all values.

## Control Flow
Values below 64 are stored in a `uint64_t` bit mask. Values 64 and above are stored in `std::set<uint32_t>`. Each operation branches on the threshold and updates or queries the appropriate backing store.

## State And Persistence
Instances hold an in-memory bit mask and set. No synchronization or persistence is provided.

## Dependencies And Integration Points
Depends on `<set>` and `<cstdint>`. It is a utility for SSI components that need sparse/mostly-small membership tracking.

## Risks And Edge Cases
Not thread-safe without external locking. The expression `1LL << bval` is safe only because `bval < 64`, but uses a signed literal; `1ULL` would avoid signed-shift concerns at bit 63.

## Test Signals
Test set/check/unset for values 0, 1, 63, 64, large values, repeated operations, reset behavior, and independence between bit-mask and set-backed ranges.
