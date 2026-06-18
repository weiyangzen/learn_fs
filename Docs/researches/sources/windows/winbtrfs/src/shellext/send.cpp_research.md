# File Research: sources/windows/winbtrfs/src/shellext/send.cpp

## Purpose
Implements Btrfs send-stream export for WinBtrfs subvolumes. It provides a GUI dialog and quiet command-line entry point that ask the driver to generate a send stream, then write a Btrfs send header, driver-provided command buffer data, and final END command to a destination file.

## Main Components
- `BtrfsSend::Thread`: GUI worker thread for stream generation.
  - Opens the source subvolume.
  - Builds `btrfs_send_subvol` with optional parent and clone handles.
  - Starts send with `FSCTL_BTRFS_SEND_SUBVOL`.
  - Writes `btrfs_send_header`.
  - Repeatedly reads send data with `FSCTL_BTRFS_READ_SEND_BUFFER`.
  - Appends a fixed checksum END command.
  - Deletes partial destination file on failure.
- `StartSend`: validates dialog input, disables controls, collects clone listbox entries, starts worker thread.
- `Browse`: save-file picker for destination stream.
- `BrowseParent`, `AddClone`: folder pickers rooted at the same volume as the source subvolume; validate selected folders are Btrfs subvolumes using `FSCTL_BTRFS_GET_FILE_IDS`.
- `RemoveClone`: removes selected clone source from the listbox.
- `SendDlgProc`: dialog procedure for write/cancel/browse/incremental/clone controls.
- `SendSubvolGUIW`: elevated GUI entry point.
- `send_subvol`: non-GUI stream writer used by quiet mode.
- `SendSubvolW`: quiet command-line entry point; parses `-p parent`, repeated `-c clone`, source subvolume, and output file.

## Data Flow
1. Entry point enables `SeManageVolumePrivilege`.
2. Source subvolume and optional parent/clone subvolumes are opened read-only for attributes.
3. Driver send is initialized with `FSCTL_BTRFS_SEND_SUBVOL`.
4. Output file receives the send header, all generated command chunks, and an END command.
5. On failure after output open, the output file is marked for deletion.

## Important Dependencies
- `shellext.h`: NT FSCTL declarations, errors, helpers.
- `send.h`: class state and declarations.
- `resource.h`: dialog/control/string IDs.
- `../btrfs.h`, `../btrfsioctl.h`: send stream and FSCTL definitions.
- Shell folder browser APIs for parent/clone selection.

## Notable Behaviors and Edge Cases
- If `FSCTL_BTRFS_SEND_SUBVOL` returns invalid parameter, GUI mode checks whether source and parent subvolumes are readonly and reports specific errors.
- GUI cancel uses `TerminateThread`, then closes active handles and deletes a partial stream if possible. This is abrupt and can bypass normal worker cleanup.
- Quiet `send_subvol` has less detailed error reporting and does not perform the same readonly-specific diagnostics.
- The END command checksum is hard-coded as `0x9dc96c50`, matching the zero-length Btrfs send END command.
