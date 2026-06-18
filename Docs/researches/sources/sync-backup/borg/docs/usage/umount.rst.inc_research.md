# sources/sync-backup/borg/docs/usage/umount.rst.inc

Purpose: Documents `borg umount`, a convenience wrapper for unmounting a FUSE filesystem created by `borg mount`.

Important APIs/types/functions: CLI contract is `borg [common options] umount [options] MOUNTPOINT` with no command-specific options.

Control flow: Runtime dispatches to the platform-specific unmount command, typically `umount` or `fusermount -u`, for the supplied mountpoint.

State and persistence: Mutates OS mount state by detaching the FUSE filesystem. It should not mutate repository contents.

Dependencies and integration points: Tightly paired with `borg mount`, libfuse/fusermount availability, and platform mount tools.

Risks: Platform differences can cause unmount failures; active processes can keep mountpoints busy. Documentation should stay aligned with supported platforms.

Test signals: Integration tests need FUSE support and should cover successful unmount, missing mountpoint, busy mountpoint, and platform command selection.
