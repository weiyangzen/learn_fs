# File Research: sources/local-fs/jfsutils/libfs/message.c

This file implements `message_user()`, a large switch-based user message printer for OS/2-derived OSO messages and JFS utility/fsck messages.

Behavior:
- Uses `msg_file == OSO_MSG` to choose a small OSO message switch.
- Otherwise prints JFS messages by numeric message ID, including mkfs, fsck, extendfs, defragfs, bad block, mount-state, superblock, map, and recovery diagnostics.
- Formats supplied parameters with `printf()` in the cases that need runtime strings.
- Unknown message numbers are silently ignored.

Integration points:
- Declared in `message.h`.
- Used by user-facing jfsutils command paths separate from `fsck_message.c`, which handles fsck/logredo structured message logging.
- Includes `debug.h` but does not use much beyond shared build context.

Risks and notes:
- `param_cnt` is unused; callers must supply enough `param[]` entries for the selected message number.
- Message IDs are partly symbolic and partly raw numeric literals, reflecting migration from an older message catalog.
- Output is direct stdout/stderr-style `printf()` text, with no localization or catalog lookup in this file.
