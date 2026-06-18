# sources/storage-engines/leveldb/util/coding.h

## Purpose
`coding.h` declares and inlines low-level encoding helpers for fixed and variable-length integers.

## Important APIs, Types, and Functions
It declares `Put*`, `Get*`, pointer decode variants, `VarintLength`, `EncodeVarint*`, and inline `EncodeFixed32`, `EncodeFixed64`, `DecodeFixed32`, `DecodeFixed64`, plus fast-path `GetVarint32Ptr`.

## Control Flow
Inline fixed encoding writes least-significant byte first. Inline fixed decoding reads bytes without bounds checks. `GetVarint32Ptr` fast-paths one-byte varints before calling fallback.

## State, Dependencies, and Integration
No runtime state. It depends on `Slice` and port declarations and is included by nearly every format-sensitive subsystem.

## Risks and Test Signals
Callers must ensure fixed decoders have enough bytes. Tests prove compatibility and malformed varint rejection.
