<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ObjectSerializer.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ObjectSerializer.h

Purpose: This header implements Flow's object serializer reader and writer wrappers around the generated flat-buffer-like serializer helpers. It gives typed objects a `StringRef` representation with optional embedded protocol version, file identifier validation, arena-aware loading, and custom allocation support.

Important APIs and types: `LoadContext<Ar>` exposes `arena`, `protocolVersion`, `tryReadZeroCopy`, and context plumbing. `_ObjectReader<ReaderImpl>` validates file identifiers and calls `load_members`. `ObjectReader` reads from external memory; `ArenaObjectReader` reads while treating the underlying arena as owning memory. `ObjectWriter` serializes one object through `save_members`, supports `AllocatorFuncType` and `MarkForWipeFuncType`, and exposes `toStringRef`, `toString`, and `toValue`. A `LoadSaveHelper<Standalone<T>, Context>` specialization makes `Standalone<T>` serialize like `T`.

Control flow: Reader constructors consume version options, which may read an embedded `ProtocolVersion`. Deserialization checks `read_file_identifier(data)` against the expected identifier and allows a logged mismatch only for a specific 7.0-to-6.3 downgrade window. Writers optionally prepend the protocol version before invoking `save_members`; `MemoryHelper` expects exactly one allocation and can mark byte ranges for wiping after use.

State and persistence behavior: The serialized bytes are persistent protocol data and include file identifiers plus optionally protocol versions. `ObjectReader` copies loaded data into its arena unless the reader owns underlying memory, while `ArenaObjectReader` can keep zero-copy references. `ObjectWriter` owns arena-backed output unless a custom allocator is supplied, in which case `toString()` is disallowed by assertion.

Dependencies and integration points: The header depends on `Error`, `Arena`, `flat_buffers.h`, `ProtocolVersion`, and trace logging for identifier mismatches. It is a central dependency for durable metadata, network messages, and structured object persistence throughout FoundationDB.

Risks: File identifier mismatches assert except for the explicit downgrade case, so adding or changing file identifiers is upgrade-sensitive. `tryReadZeroCopy` behavior depends on ownership and can create lifetime hazards if callers choose the wrong reader. The writer's single-allocation invariant is strict and will assert if serializer internals change. Custom allocator and wipe hooks are low-level and require careful lifetime management.

Test signals: Strong tests include object round trips with and without embedded versions, file identifier mismatch behavior, old-version downgrade logging, zero-copy versus arena-copy lifetime cases, custom allocator size and wipe callback invocation, and `Standalone<T>` equivalence to `T` serialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ObjectSerializer.h -->
