<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/colblk_64bit_test.go -->
# sources/storage-engines/pebble/sstable/colblk/colblk_64bit_test.go

## Purpose
`colblk_64bit_test.go` is a compile-time guard for 64-bit platforms. It verifies that `block.MetadataSize` is not larger than required for the columnar data-block decoder and key-seeker metadata payload.

## Important APIs, Types, And Functions
The file contains a single build-tagged constant assertion:
`const _ uint = uint(unsafe.Sizeof(blockDecoderAndKeySeekerMetadata{})) - block.MetadataSize`. This fails compilation if `block.MetadataSize` grows beyond the exact size of `blockDecoderAndKeySeekerMetadata` on `arm64` or `amd64`.

## Control Flow
There is no runtime control flow. The Go type checker evaluates the constant expression during compilation. If the subtraction underflows, compilation fails.

## State And Persistence Behavior
This file does not persist data, but it protects in-memory block-cache layout. `blockDecoderAndKeySeekerMetadata` is stored inside `block.Metadata`, so unnecessary metadata growth can increase every cached block allocation.

## Dependencies And Integration Points
The assertion couples `data_block.go`'s metadata struct with `sstable/block.MetadataSize`. It is intentionally architecture-specific because pointer and alignment sizes differ across platforms.

## Risks
The guard is strict: legitimate future growth of `block.MetadataSize` for unrelated consumers would require updating or rethinking this assertion. It only covers `arm64` and `amd64`, not all supported architectures.

## Test Signals
The signal is compilation success. It complements the more general compile-time assertions in `data_block.go` that the metadata struct fits and is aligned.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/colblk_64bit_test.go -->
