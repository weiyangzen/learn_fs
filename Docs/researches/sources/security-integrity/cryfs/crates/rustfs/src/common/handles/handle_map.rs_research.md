# sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_map.rs

Purpose: stores async-droppable objects by generated handles, coupling a `HandlePool` with an async-drop hash map.

Important APIs: `HandleMap::new`, `add`, `remove`, `get`, feature-gated `iter`, and `AsyncDrop`.

Control flow and state: `add` acquires a handle with generation, inserts the object by bare handle, and returns `HandleWithGeneration`. `remove` deletes the object and releases the handle for future reuse with incremented generation. `get` returns an optional guard reference. `AsyncDrop` delegates to the inner `AsyncDropHashMap`.

Dependencies and integration: used by `OpenFileList` and `DirCache`. Depends on `HandlePool`, `HandleWithGeneration`, `HandleTrait`, `AsyncDropGuard`, and `FsError`.

Risks and tests: duplicate insert and missing remove panic. The map keys only by handle, not generation, so callers must not use stale handles after release; generation is returned for diagnostics and inode replies but not validated here. TODO suggests a slab/vector optimization and tests.
