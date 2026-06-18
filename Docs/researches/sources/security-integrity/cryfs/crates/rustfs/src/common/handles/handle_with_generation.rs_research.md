# sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_with_generation.rs

Purpose: couples a handle value with a generation counter.

Important APIs: `HandleWithGeneration<Handle> { handle, generation }`, clone/copy/equality/hash/debug/display.

Control flow and state: plain data. Display formats as `handle.generation`, useful in logs and FUSE reply debugging.

Dependencies and integration: returned by `HandlePool`, `HandleMap`, `InodeList`, and reply structs. Generation increases when a handle is released and later reused.

Risks and tests: generation does not enforce stale-handle rejection by itself because maps generally key by bare handle. It is most useful where the kernel or tests track inode lookup generations.
