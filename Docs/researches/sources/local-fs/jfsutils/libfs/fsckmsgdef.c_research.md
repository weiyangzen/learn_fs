# File Research: sources/local-fs/jfsutils/libfs/fsckmsgdef.c

## Purpose
Instantiates the global fsck/logredo message catalog declared in `fsck_message.h`.

## Main Artifact
`struct fsck_message msg_defs[fsck_highest_msgid_defined + 1]` contains entries `0` through `599`.

## Content Coverage
- Early IDs cover general fsck success/failure, root directory errors, superblock corruption, inode/link/directory problems, duplicate blocks, allocation-map inconsistencies, device and mount messages, and phase banners.
- Midrange IDs include inode allocation map and block allocation map diagnostics, heartbeat text, directory index messages, bad-block/LVM transfer messages, and xchklog/xchkdmp output errors.
- IDs `384-399` are text insertion tokens such as object prefixes (`A`, `D`, `DM`, `F`, `I`, `L0`, `L1`, `L2`, `M`).
- IDs `400-599` cover logredo status and failures: log-end detection, journal superblock validation, replay initialization, map rebuild/writeback, page redo/no-redo handling, buffer reads, and end-of-log/page validation.

## Compatibility Details
- Undefined slots are explicitly present as `*undefined*`.
- A comment states IDs `424-430` should no longer be used but remain defined so fscklog can read older logs.

## Dependencies
Includes `config.h` and `fsck_message.h`; all message numeric constants and levels come from the header.

## Notes
This file is data-only. Message text format specifiers must stay synchronized with all `fsck_send_msg()` call sites; mismatches would be runtime formatting bugs.
