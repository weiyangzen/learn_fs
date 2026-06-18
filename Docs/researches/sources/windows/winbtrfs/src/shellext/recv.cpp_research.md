# File Research: sources/windows/winbtrfs/src/shellext/recv.cpp

## Purpose
Implements WinBtrfs receive support for Btrfs send streams. It provides both GUI and command-line `rundll32` entry points that replay a send stream into a target directory by creating or snapshotting subvolumes, applying filesystem mutations, validating command checksums, and finalizing the received subvolume through WinBtrfs private FSCTLs.

## Main Components
- `BtrfsRecv::Open`: stores the stream path and destination path, chooses GUI progress dialog or quiet mode, and enables hardware CRC32C on x86/x64 when SSE4.2 is available.
- `BtrfsRecv::recv_thread`: opens the send-stream file and destination directory, loops over one or more send streams in the file, and updates dialog state.
- `BtrfsRecv::do_recv`: core stream interpreter. Reads `btrfs_send_header`, validates magic/version, reads each `btrfs_send_command`, verifies CRC32C, dispatches supported send commands, detects truncation, handles cancellation, and calls `FSCTL_BTRFS_RECEIVED_SUBVOL` at completion.
- Command handlers:
  - `cmd_subvol`, `cmd_snapshot`: create the received root with `FSCTL_BTRFS_CREATE_SUBVOL` or `FSCTL_BTRFS_CREATE_SNAPSHOT`, reserve it with `FSCTL_BTRFS_RESERVE_SUBVOL`, open working handles, and cache UUID/transid to path mappings.
  - `cmd_mkfile`: handles regular files, dirs, special nodes, FIFOs, sockets, and symlinks. Symlinks are created as Win32 reparse points and then have POSIX mode set.
  - `cmd_rename`, `cmd_link`, `cmd_unlink`, `cmd_rmdir`: replay namespace changes through Win32 file APIs.
  - `cmd_setxattr`, `cmd_removexattr`: maps most `user.*` xattrs to NTFS alternate data streams, while special xattrs such as `security.NTACL`, `user.DOSATTRIB`, `user.reparse`, and `user.EA` go through `FSCTL_BTRFS_SET_XATTR`.
  - `cmd_write`, `cmd_clone`, `cmd_truncate`: write file data, duplicate extents from clone sources with `FSCTL_DUPLICATE_EXTENTS_TO_FILE`, and resize files.
  - `cmd_chmod`, `cmd_chown`, `cmd_utimes`: apply mode/ownership/timestamps through WinBtrfs inode info FSCTLs or NT file information.
- Exported callbacks:
  - `RecvSubvolGUIW`: GUI entry point; prompts for a send-stream file and receives into the command-line destination.
  - `RecvSubvolW`: quiet command-line entry point; parses stream and destination from command line.

## Data Flow
1. Entry point enables required privileges: `SeManageVolumePrivilege`, `SeSecurityPrivilege`, and `SeRestorePrivilege`.
2. Stream file is opened read-only and destination directory is opened with create permissions.
3. Each stream command’s TLV payload is parsed with `find_tlv`.
4. The command is replayed relative to the current received subvolume path.
5. On success, the received subvolume UUID/generation are committed with `FSCTL_BTRFS_RECEIVED_SUBVOL`.
6. On error, any partially created received subvolume path is made writable and recursively deleted.

## Important Dependencies
- `shellext.h`: Win32/NT prototypes, RAII handles, errors, encoding helpers.
- `recv.h`: class state and declarations.
- `resource.h`: localized error/status IDs.
- `../btrfs.h`, `../btrfsioctl.h`: send-stream structures, Btrfs types, WinBtrfs FSCTL codes.
- `../crc32c.h`: software/hardware CRC32C dispatch.

## Notable Behaviors and Edge Cases
- Stream validation checks magic, version `<= 1`, per-command CRC32C, and payload length against file size.
- `BTRFS_SEND_CMD_UPDATE_EXTENT` is accepted but intentionally ignored.
- Consecutive writes to the same file reuse `lastwritefile`; readonly attributes are temporarily cleared and restored.
- Clone sources are resolved first from an in-memory UUID/transid cache, then via `FSCTL_BTRFS_FIND_SUBVOL`.
- GUI cancellation sets `cancelling`; partial output cleanup still occurs through the common exception path only for thrown failures, while the loop itself exits gracefully when cancellation is noticed.
- Several manually allocated FSCTL request buffers are not consistently freed after successful use, so this file has small process-lifetime leak potential during receive operations.
