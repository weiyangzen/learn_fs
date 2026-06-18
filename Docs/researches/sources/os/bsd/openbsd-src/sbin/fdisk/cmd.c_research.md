# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/cmd.c

## Purpose
Implements interactive `fdisk` commands shared by GPT and MBR editing modes.

## Key Behavior
- `Xreinit()` reinitializes the current table as GPT or MBR and marks the session dirty.
- `Xswap()` swaps two GPT partition entries or two MBR partition entries.
- `Xedit()` edits a selected partition, or for GPT can recover a partition from a description string.
- `gedit()` edits GPT partition type, start LBA, end LBA/size, and name.
- `edit()` edits MBR partition type and either CHS boundaries or LBA offset/size.
- `Xsetpid()` changes only partition type/id.
- `Xselect()` descends into an extended MBR partition and edits its EMBR.
- `Xprint()` prints GPT, MBR, or geometry/no-table state.
- `Xwrite()` writes GPT or MBR, warns if multiple OpenBSD MBR partitions exist, and zaps GPT headers when writing MBR.
- `Xflag()` sets raw GPT attrs/MBR flags or marks one partition active/bootable.
- `Xmanual()` displays the embedded compressed manual through `$PAGER` or `/usr/bin/less`.
- `ask_num()`, `ask_pid()`, and `ask_uuid()` provide interactive prompts and validation.
- `parsepn()` validates partition indices based on GPT partition count or MBR slot count.
- `parseflag()` accepts decimal or hex GPT/MBR flag values.

## Notes
This file is the command adapter between user intent and the lower GPT/MBR/disk primitives. It avoids modifying protected GPT partition types.
