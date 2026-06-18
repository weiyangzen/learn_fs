# sources/security-integrity/cryfs/crates/rustfs/src/backend/fuse_mt/mount.rs

Purpose: Mount orchestration for the `fuse_mt` backend.

Important APIs/types/functions: `mount` spawns the backend, invokes the success callback, optionally installs unmount trigger, and blocks until unmounted. `spawn_mount` builds `BackendAdapter`, wraps it in `FuseMT`, translates fuser 0.17 `Config` to fuser 0.16 options, and calls `fuser_fusemt::spawn_mount2`. Helpers choose thread count and convert mount options.

Control flow: on spawn failure it manually calls `destroy` and async-drops the backend because fuser will not call destroy. On success it drops the internal arc and returns `RunningFilesystem`.

State and persistence behavior: state is the background FUSE session and guarded filesystem. No persistence beyond delegated filesystem.

Dependencies and integration points: used by `backend/fuse_mt/mod.rs`; depends on `RunningFilesystem`, `BackendAdapter`, `FuseMT`, and cancellation tokens.

Risks: manual cleanup path uses `unwrap` during async drop. Thread count defaults to available parallelism or 2. Config translation must stay aligned with fuser versions.

Test signals: mount failure cleanup tests, option translation tests, and cancellation-trigger unmount tests are valuable.
