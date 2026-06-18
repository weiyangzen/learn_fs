# sources/storage-engines/leveldb/util/crc32c.h

## Purpose
`crc32c.h` declares CRC32C calculation and masking helpers.

## Important APIs, Types, and Functions
`Extend`, inline `Value`, `Mask`, `Unmask`, and `kMaskDelta` are provided under `leveldb::crc32c`.

## Control Flow
`Value` calls `Extend(0, ...)`. `Mask` rotates right by 15 bits and adds a constant; `Unmask` reverses that operation.

## State, Dependencies, and Integration
No state. Masked CRCs are stored in table block trailers so embedded CRC bytes do not create fragile self-referential patterns.

## Risks and Test Signals
Changing mask math is an on-disk compatibility break. CRC tests verify masking is reversible and not idempotent.
