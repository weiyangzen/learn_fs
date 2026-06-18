# sources/storage-engines/rocksdb/table/block_based/flush_block_policy_impl.h

## Purpose
Declares internal flush block policies used by block-based table building and tests. It includes a deterministic every-key policy and a retargetable base used when one policy object must follow different `BlockBuilder` instances.

## Important APIs, Types, And Functions
`FlushBlockEveryKeyPolicy` returns false for the first key and true for every subsequent key. `FlushBlockEveryKeyPolicyFactory` creates that policy and exposes `kClassName`. `RetargetableFlushBlockPolicy` stores a `BlockBuilder` pointer and exposes `Retarget`. `NewFlushBlockBySizePolicy` constructs a size-based retargetable policy.

## Control Flow
The every-key policy is stateful only for the first update. Retargetable policies are constructed with one block builder and can later be redirected before update checks, which lets partitioned index code reuse one flush-policy object across sub-index builders.

## State And Persistence Behavior
No persistence occurs in this header. The every-key policy stores a boolean `start_`; the retargetable base stores a non-owning `BlockBuilder` pointer.

## Dependencies And Integration Points
Depends on public `rocksdb/flush_block_policy.h` and is implemented by `flush_block_policy.cc`. Used by table-builder code, tests, and partitioned index builder partition cutting.

## Risks And Edge Cases
Because the retargeted builder pointer is non-owning, lifetime and retarget timing are critical. The every-key policy is intended for tests, not production tuning, because it creates very small blocks.

## Test Signals
Factory registration and block-boundary tests can force one key per block. Partitioned-index tests exercise retargeting through size-policy reuse.
