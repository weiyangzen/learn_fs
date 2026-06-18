# sources/storage-engines/rocksdb/include/rocksdb/flush_block_policy.h

## Purpose

`flush_block_policy.h` defines the configurable policy that tells block-based table builders when to finish the current data block and start another. It is the extension point behind block boundary decisions.

## Important APIs, types, and functions

`FlushBlockPolicy` exposes one method, `Update(const Slice& key, const Slice& value)`, which tracks the key/value stream and returns whether the current block should be flushed. `FlushBlockPolicyFactory : public Customizable` creates policies with `CreateFromString` and virtual `NewFlushBlockPolicy(table_options, data_block_builder)`. `FlushBlockBySizePolicyFactory` is the built-in size-based factory with class name `FlushBlockBySizePolicyFactory` and static construction helper accepting target size, deviation, and `BlockBuilder`.

## Control flow and behavior

During table building, each added key/value is passed to the active policy. The policy inspects accumulated block-builder state and the incoming record, then returns true when the block should be emitted. The factory is configured in table options and creates a fresh policy per data block builder context. Built-in string loading supports default EveryKey or BySize policies.

## State and persistence

Policy objects own transient state about the current block and key/value sequence. They do not directly persist metadata, but their decisions determine data block boundaries in SST files, which affects index layout, compression, cache behavior, read amplification, and filter granularity.

## Dependencies and integration points

The header depends on `Customizable` and `table.h`, and forward-declares `Slice`, `BlockBuilder`, `ConfigOptions`, and `Options`. It integrates with `BlockBasedTableOptions`, block-based table builders, configurable option parsing, and any code that relies on predictable block sizes.

## Risks and test signals

Custom policies must not throw exceptions and must avoid decisions that produce pathological tiny or huge blocks unless intentionally configured. They must treat `key` and `value` as transient inputs and rely on builder metadata carefully. Tests should cover factory string creation, default by-size behavior, deviation handling, EveryKey behavior if configured, block size distribution, and table read correctness after custom flush boundaries.
