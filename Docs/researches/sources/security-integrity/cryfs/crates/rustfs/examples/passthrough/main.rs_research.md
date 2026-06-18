# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/main.rs

Purpose: Example binary that mounts a host-directory passthrough filesystem.

Important APIs/types/functions: parses `basedir` and `mountdir`, constructs `PassthroughDevice`, wraps it in `ObjectBasedFsAdapterLL`, and mounts through `backend::fuser::mount`.

Control flow: synchronous `main` initializes logging, validates two arguments, builds a multi-thread Tokio runtime, and blocks on mount until unmounted.

State and persistence behavior: all changes persist in the provided base directory.

Dependencies and integration points: demonstrates passthrough object API over the low-level fuser backend.

Risks: argument parsing and path conversion use `expect`/`unwrap`; malformed paths panic. No cancellation token is supplied. Running this example can modify/delete real files under `basedir`.

Test signals: build plus controlled temporary-directory mount tests are appropriate.
