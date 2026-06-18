# sources/storage-engines/rocksdb/table/block_based/flush_block_policy.cc

## Purpose
Implements block flush policy factories for block-based table building. The main policy cuts data or metadata blocks based on estimated block size, optional deviation thresholds, and block-alignment settings.

## Important APIs, Types, And Functions
`FlushBlockBySizePolicy` implements `FlushBlockPolicy::Update` and private `BlockAlmostFull`. `FlushBlockBySizePolicyFactory::NewFlushBlockPolicy` creates policies from table options or explicit size/deviation parameters. `NewFlushBlockBySizePolicy` returns a retargetable size policy for internal partitioned-index use. `RegisterFlushBlockPolicyFactories` registers size and every-key factories. `FlushBlockPolicyFactory::CreateFromString` loads policies through the object registry.

## Control Flow
`Update` refuses to flush an empty block. It then checks whether the current estimate already exceeds `block_size_` or whether appending the candidate key/value would exceed the target while the current block is past the deviation limit. With block alignment enabled, it adds the block trailer size before comparing to the target.

## State And Persistence Behavior
Policy state is transient: target block size, computed deviation limit, alignment flag, and a pointer to the current `BlockBuilder` supplied by the retargetable base. It influences on-disk block boundaries but does not write bytes itself.

## Dependencies And Integration Points
Depends on public flush policy interfaces, block-based table options, `BlockBuilder` size estimates, block trailer size, and object-library registration. Partitioned index construction uses `NewFlushBlockBySizePolicy` and retargets it as new sub-index builders are created.

## Risks And Edge Cases
Incorrect size estimates can produce blocks larger or smaller than expected, but correctness is preserved. Empty-block protection prevents infinite flush loops. Retargetable policies must always point to a live builder before `Update` is called.

## Test Signals
Coverage is indirect through block-builder/table-builder tests, partitioned index partition-size tests, and configurable factory loading tests. `FlushBlockEveryKeyPolicyFactory` supports deterministic test block boundaries.
