# File Research: sources/windows/winbtrfs/src/shellext/scrub.h

## Purpose
Declares the `BtrfsScrub` dialog/controller class used by `scrub.cpp`.

## Main Components
- Constructor stores the target drive/path in `fn`.
- Public `ScrubDlgProc` handles dialog messages.
- Private helpers refresh state, render scrub text, and start/pause/stop scrub.

## State
- `wstring fn`: target volume/path.
- `uint32_t status`: last known scrub status.
- `uint64_t chunks_left`: last known remaining chunk count.
- `uint32_t num_errors`: last known error count.

## Dependencies
Includes Windows APIs plus `../btrfs.h` and `../btrfsioctl.h`.

## Notable Behavior
The class caches prior status/chunk/error values so dialog refreshes can avoid unnecessary text and control updates.
