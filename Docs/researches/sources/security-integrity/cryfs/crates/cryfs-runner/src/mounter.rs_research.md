# sources/security-integrity/cryfs/crates/cryfs-runner/src/mounter.rs

## Purpose
Provides a small strategy enum for running mounts in foreground or through a background daemon.

## Important APIs, types, and functions
- `Mounter::{MountInForeground, MountInBackgroud}` selects execution mode.
- `run_in_foreground` creates foreground mode.
- `run_in_background` daemonizes and bootstraps logging through `BackgroundProcess`.
- `mount_filesystem` delegates to foreground runner or background RPC.

## Control flow
Foreground mode awaits `runner::mount_filesystem`, which blocks until unmount. Background mode sends mount args over RPC, returns after successful mount response, then calls the success callback locally.

## State and persistence behavior
Foreground holds no daemon state. Background stores a `BackgroundProcess` RPC client. Persistence is delegated to runner/filesystem layers.

## Dependencies and integration points
Integrates CLI logging config, `MountArgs`, `BackgroundProcess`, and `runner::mount_filesystem`. It is the high-level API used by the CLI to choose daemon mode.

## Risks and edge cases
The enum variant name contains a typo (`MountInBackgroud`), which is harmless but public within the crate. In background mode, the callback is invoked after RPC mount success, not after the daemon eventually unmounts.

## Test signals
Signals should cover foreground blocking semantics, background early-return semantics, daemon bootstrap failure propagation, and callback ordering.
