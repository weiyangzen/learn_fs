# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/maybe_initialized_fs.rs

Purpose: stores a filesystem constructor until FUSE init supplies uid/gid, then exposes the initialized filesystem.

Important APIs: `MaybeInitializedFs::new_uninitialized`, `initialize`, `get`, custom debug, and `AsyncDrop`.

Control flow and state: enum state is either `Uninitialized(Some(Box<FnOnce(Uid, Gid) -> Fs>))` or `Initialized(AsyncDropGuard<Fs>)`. `initialize` consumes the constructor and changes state. `get` panics if called before init. Async drop drops the initialized filesystem, or if still uninitialized, calls the constructor with uid/gid zero and drops the result.

Dependencies and integration: used by high and low object adapters to delay device creation until request identity is known.

Risks and tests: calling the constructor on drop with dummy ids may have side effects even if init never occurred. Double init and pre-init get panic. TODOs question whether initialization storage can be simplified.
