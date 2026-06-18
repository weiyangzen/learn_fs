# sources/user-network-fs/libfuse/lib/mount_common_i.h

## Purpose
Internal cross-platform mount interface shared by Linux, BSD, and utility code. It hides the platform-specific definition of `struct mount_opts` while exposing lifecycle and option inspection functions.

## Important APIs, Types, And Functions
- Forward declares `struct fuse_args` and opaque `struct mount_opts`.
- Defines `FUSE_MOUNT_FALLBACK_NEEDED` as `-2` for direct mount callers that should retry through `fusermount3`.
- Declares `parse_mount_opts`, `destroy_mount_opts`, `get_max_read`, `fuse_mnt_kernel_opts`, `fuse_mnt_mtab_opts`, and `fuse_mnt_flags`.

## Control Flow
No executable flow; it establishes the ABI contract consumed by libfuse mounting code and platform-specific implementation files.

## State And Persistence
No state. Ownership conventions are important: parser returns allocated `mount_opts`; string getters return duplicated strings where implemented.

## Dependencies And Integration Points
Included by `mount_util.h`, Linux/BSD mount implementations, and code that needs mount option metadata without knowing platform internals.

## Risks
Because `struct mount_opts` is opaque here but concrete in platform headers, mismatched includes or platform-specific assumptions can become compile-time or ABI issues. The fallback sentinel must not collide with normal fd returns.

## Test Signals
Compile Linux and BSD variants, verify fallback handling treats `-2` distinctly from `-1`, and run option parser lifecycle tests under leak sanitizers.
