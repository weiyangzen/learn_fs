<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/shared_memory.rs -->
## sources/object-store/rustfs/crates/io-core/src/shared_memory.rs

### Purpose
Provides Arc-backed shared data wrappers and a lightweight pool facade for zero-copy-style cross-task sharing. It avoids cloning the underlying payload by wrapping data in `ArcData<T>` and cloning the `Arc`.

### Important APIs, Types, And Functions
`SharedMemoryConfig` configures enablement, maximum pool size, and maximum object size. `SharedMemoryStats` stores atomic totals for created objects, shared references, current memory, and peak memory. `ArcMetadata` records optional size and creation time. `ArcData<T>` wraps `Arc<T>` and metadata, with `new`, `with_size`, `ref_count`, `into_arc`, `metadata`, `size`, `AsRef`, `Deref`, and `Debug`. `SharedMemoryPool` exposes `create`, `create_with_size`, `share`, `stats`, `config`, and `is_enabled`.

### Control Flow
`create` increments `total_objects` and returns `ArcData::new`. `create_with_size` increments object count, adds the supplied size to `current_memory`, updates `peak_memory` if the current total is greater, and returns `ArcData::with_size`. `share` increments `total_shared_refs` and clones the `ArcData`.

### State And Persistence
All state is in atomic counters inside `SharedMemoryPool`; there is no persistent storage. `ArcData` carries metadata for the lifetime of the wrapper. Memory counters are observational and do not own allocation lifecycle.

### Dependencies And Integration Points
Depends only on the standard library (`Arc`, atomics, `Instant`, traits). Intended to integrate with zero-copy readers/writers and metrics paths that need shared ownership without serialization.

### Risks
`SharedMemoryConfig.enabled`, `max_pool_size`, and `max_object_size` are exposed but not enforced by `create` or `create_with_size`. `current_memory` only increases and is never decremented when `ArcData` drops, so it is not an accurate live-memory gauge. Peak update uses load/store rather than CAS, so concurrent creators can race and lose a higher peak. The metadata size is caller-provided and not validated against actual payload size.

### Test Signals
Tests cover `ArcData` creation, clone/reference count behavior, deref access, pool creation/share counters, size metadata, current-memory increment, and default config values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/shared_memory.rs -->
