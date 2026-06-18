# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/main.rs

Purpose: Example binary that mounts the in-memory filesystem through the fuser backend.

Important APIs/types/functions: declares example modules, parses one mountdir argument, builds a Tokio runtime, constructs `InMemoryDevice` from request uid/gid, wraps it in `ObjectBasedFsAdapterLL`, and calls `backend::fuser::mount`.

Control flow: synchronous `main` initializes logging, validates arguments with `expect`/`assert`, then blocks on async mount until unmounted.

State and persistence behavior: filesystem contents are volatile and recreated at process start.

Dependencies and integration points: demonstrates object-based API to low-level adapter to fuser backend flow.

Risks: argument parsing is minimal, runtime `unwrap`s panic on failures, and no cancellation token is provided. Calls to unimplemented filesystem operations such as `statfs` may panic.

Test signals: build the example and smoke mount/unmount in an environment with FUSE support.
