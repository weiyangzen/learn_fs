# sources/storage-engines/pebble/sstable/rowblk/rowblk_writer.go

## Purpose
Serializes key/value pairs into Pebble's row-oriented block format: prefix-compressed entries followed by restart offsets and a restart count. It is the low-level encoder used for data, index, range deletion, range key, properties, and raw blocks.

## Important APIs, Types, And Functions
`Writer` exposes `Reset`, `EntryCount`, `CurKey`, `CurValue`, `CurUserKey`, `Add`, `AddWithOptionalValuePrefix`, `Finish`, `EstimatedSize`, `AddRaw`, and `AddRawString`. Constants include `MaximumRestartOffset`, `EmptySize`, `TrailerObsoleteBit`, `TrailerObsoleteMask`, and `ErrBlockTooBig`. `storeWithOptionalValuePrefix` performs the actual varint, key, optional value-prefix, value, and restart encoding.

## Control Flow And State
Each add swaps `curKey` and `prevKey`, encodes the internal key, optionally sets the obsolete bit, computes a shared prefix up to `maxSharedKeyLen`, appends a restart offset when `nEntries == nextRestart`, and writes three varints followed by unshared key bytes and value bytes. For Pebblev3 data blocks, `setHasSameKeyPrefixSinceLastRestart` is accumulated and encoded into the high bit of restart offsets; `maxSharedKeyLen` limits key sharing to the previous key prefix so `NextPrefix` can skip efficiently.

`Finish` ensures even an empty block has one restart point, appends all restart offsets and the restart count, returns the encoded block, and clears per-block counters/buffers for reuse. `Reset` fully resets state while preserving allocated slices.

## Persistence And Integration
The writer produces the persistent bytes read by `rowblk.Iter` and described by `sstable/table.go`. It integrates with `RawRowWriter`, suffix rewriting, properties serialization, range-key/range-delete blocks, and value-block prefix metadata. The obsolete bit is internal to row-block encoding and masked away when reading current keys.

## Dependencies
Uses `base.InternalKey` encoding, `block.ValuePrefix` for v3 value/value-block metadata, `errors` for corruption-sized block reporting, and unsafe string-to-byte conversion in `AddRawString`.

## Risks
`RestartInterval` must be configured by callers; an interval of zero would make restart scheduling invalid. Blocks cannot exceed `MaximumRestartOffset` because one restart bit is reserved for prefix metadata. The high-bit restart flag and obsolete trailer bit are format-internal and must stay consistent with `Iter.decodeRestart` and trailer masking. Manual varint and shared-prefix encoding is performance-sensitive and assumes keys are added in sorted order by higher layers.

## Test Signals
`rowblk_writer_test.go` verifies reset semantics, exact byte layout for raw prefix compression, optional value-prefix encoding, and high-bit restart metadata. Iterator and suffix rewrite tests also validate that written blocks can be read and transformed correctly.
