# File Research: sources/os/linux/linux-stable/fs/smb/client/fs_context.h

## Summary
Defines the CIFS/SMB3 fs_context data model, mount-option enums, shared mount parsing helpers, mount-context API declarations, mount mutex helpers, and negotiated I/O size helpers used by SMB client mount and file I/O code.

## Main Responsibilities
- Provide `cifs_errorf()` so fs_context errors are reported both through mount API diagnostics and CIFS debug logging.
- Align user-supplied I/O sizes to page-size boundaries through `cifs_io_align()` and `CIFS_ALIGN_*` macros.
- Enumerate supported SMB dialect tokens, cache flavors, reparse flavors, symlink flavors, security flavors, upcall targets, and mount parameter IDs.
- Define `struct smb3_fs_context`, the complete parsed mount configuration.
- Declare mount-context lifecycle and utility functions implemented in `fs_context.c`.
- Provide default symlink policy resolution from explicit mount options, mfsymlinks/SFU/Linux extension state, POSIX extension negotiation, and reparse policy.
- Provide mount mutex wrappers and negotiated read/write size helpers.

## Key Structures And APIs
- `struct smb3_fs_context` stores authentication fields, UNC/source/prepath state, NetBIOS names, uid/gid/mode choices, security/upcall settings, cache and permission booleans, protocol operations/value tables, network addresses, NLS state, timeouts, rsize/wsize/bsize/rasize, multichannel state, fscache/compression/witness/rootfs flags, DFS state, reparse/symlink policy, and symlink root.
- `smb3_fs_parameters[]` is declared for the parser table.
- `smb3_init_fs_context()`, `smb3_cleanup_fs_context_contents()`, `smb3_cleanup_fs_context()`, `smb3_fs_context_dup()`, `smb3_sync_session_ctx_passwords()`, and `smb3_update_mnt_flags()` are exported within the client.
- `smb3_fc2context()` casts `fs_context->fs_private` to the SMB context.
- `cifs_symlink_type()` computes the effective symlink implementation.
- `cifs_mount_lock()` and `cifs_mount_unlock()` wrap the global mount mutex.
- `cifs_negotiate_rsize()`, `cifs_negotiate_wsize()`, and `cifs_negotiate_iosize()` clamp negotiated sizes to at least one page and to user-specified maximums when present.

## Important Behavior
The option enum mirrors the parser table in `fs_context.c`; changes must stay synchronized or options will be parsed into the wrong behavior. The context contains many single-bit booleans that later become `CIFS_MOUNT_*` flags or protocol decisions, so it is the central handoff object between mount parsing and the rest of the CIFS client.

The symlink helper prefers an explicitly requested symlink type. Without one, it chooses mfsymlinks, SFU symlinks, native or Unix symlinks depending on Linux/POSIX extension state, native SMB symlinks when reparse handling is enabled, or no symlink support.

The negotiated I/O size helpers call protocol-specific `server->ops` hooks and then round sizes down to a page multiple. They mutate the mount context lazily when `file.c` prepares first reads/writes and finds `rsize` or `wsize` still unset.

## Dependencies And Invariants
This header depends on CIFS global types, Linux fs_parser, and parser definitions. It must remain in sync with `fs_context.c` cleanup/duplication code because every owned string in `struct smb3_fs_context` needs matching duplicate and cleanup handling. Size alignment assumes page-sized netfs I/O granularity. `SMB3_MAX_DCLOSETIMEO`, `SMB3_DEF_DCLOSETIMEO`, and `MAX_CACHED_FIDS` define defaults and bounds consumed by mount parsing and deferred close logic.

## Risks
Adding a mount option requires coordinated updates to the enum, parser table, parse switch, defaults, cleanup/duplication if new owned data is added, and mount flag translation if it affects runtime flags. The large context structure is widely shared, so ownership mistakes in string fields or stale defaults on remount can produce subtle leaks, use-after-free, or configuration drift.
