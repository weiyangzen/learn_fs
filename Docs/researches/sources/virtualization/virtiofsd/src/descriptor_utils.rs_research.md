# File Research: sources/virtualization/virtiofsd/src/descriptor_utils.rs

## Scope

Utilities that expose virtqueue descriptor chains as high-level `Read` and `Write` streams over guest memory. This is the bridge between vhost-user virtio queue buffers and Rust/FUSE request handling.

## APIs Covered

- `Error` and `Result` for descriptor memory, overflow, split, and I/O failures.
- Internal `DescriptorChainConsumer` over `VecDeque<VolatileSlice>`.
- `Reader` for device-readable descriptors.
- `Writer` for device-writable descriptors.
- `DescriptorType` test helper enum.

## Behavior

- `Reader::new()` collects readable descriptors until the first writable descriptor, resolving guest addresses into volatile memory slices.
- `Writer::new()` collects writable descriptors.
- Both constructors check combined descriptor lengths for `usize` overflow.
- `read_obj()` and `write_obj()` move `ByteValued` protocol structs across descriptor memory.
- `write_to_file_at()` and `read_from_file_at()` use volatile vectored I/O for zero-copy file transfer.
- `split_at()` divides a reader/writer at byte offsets, preserving descriptor boundaries or splitting a volatile slice.
- `Writer` marks guest-memory dirty bitmap ranges after writes.

## Tests And Invariants

Tests cover simple read/write chains, incompatible descriptor types, shared readable/writable chains, object values split byte-by-byte across descriptors, EOF behavior, split edge cases, out-of-bounds split errors, and short full-buffer reads/writes. The main invariant is that descriptor consumption only advances after the closure succeeds.
