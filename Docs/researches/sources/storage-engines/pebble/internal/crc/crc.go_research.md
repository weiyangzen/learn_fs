# sources/storage-engines/pebble/internal/crc/crc.go

## Purpose
This file implements Pebble's RocksDB-compatible CRC-32C checksum wrapper.

## Important APIs, Types, And Functions
Package-level `table` is a Castagnoli CRC table. `type CRC uint32` provides `New`, `Update`, and `Value`.

## Control Flow
`New` starts with zero CRC and updates with bytes. `Update` calls `crc32.Update` using the Castagnoli table. `Value` applies RocksDB-style masking by rotating right 15/left 17 and adding `0xa282ead8`.

## State And Persistence Behavior
The table is immutable package state. Checksums are stored by callers in little-endian format; this file only computes the uint32 value.

## Dependencies And Integration Points
It depends on Go's `hash/crc32`. It is used throughout Pebble for record/block checksum verification and compatibility with LevelDB/RocksDB checksum masking.

## Risks And Edge Cases
Changing the polynomial, masking rotation, or delta would break on-disk compatibility. The wrapper is simple but persistence-critical.

## Test Signals
No direct tests are listed in this subset. Indirect coverage comes from manifest/log/table read-write tests elsewhere that validate checksum round-trips and corruption detection.
