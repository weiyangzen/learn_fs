# sources/security-integrity/cryfs/crates/rustfs/src/backend/fuser/mount.rs

Purpose: Mount orchestration for the primary fuser backend.

Important APIs/types/functions: `mount` wraps `spawn_mount`, invokes a success callback, optionally wires a `CancellationToken` unmount trigger, and blocks until unmount. `spawn_mount` creates `BackendAdapter`, calls `fuser::spawn_mount2`, and returns `RunningFilesystem`.

Control flow: as in fuse_mt, the code keeps an internal arc so failed mount setup can manually destroy and async-drop the filesystem. Successful spawn transfers lifecycle to fuser destroy/drop handling.

State and persistence behavior: session state is held by fuser's background session; filesystem persistence is delegated to `AsyncFilesystemLL`.

Dependencies and integration points: used by examples and backend facade; depends on `RunningFilesystem`, `BackendAdapter`, fuser config, and cancellation tokens.

Risks: mount failure cleanup has to mirror normal destroy exactly. Async drop failure handling uses unwrap in the failure path. `mount` blocks the caller after success until unmounted.

Test signals: mount failure cleanup, success callback ordering, cancellation-trigger unmount, and smoke operations through a mounted filesystem.
