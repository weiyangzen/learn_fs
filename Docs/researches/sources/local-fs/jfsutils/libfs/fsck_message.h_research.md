# File Research: sources/local-fs/jfsutils/libfs/fsck_message.h

## Purpose
Defines the message-number namespace, severity/verbosity levels, text-insertion tokens, and message-dispatch macros for JFS fsck and logredo.

## Interface
- Globals: `msg_lvl`, `dbg_output`, and `msg_defs[]`.
- Dispatch functions: `v_fsck_send_msg()` and `v_send_msg()`.
- Convenience macros: `fsck_send_msg(msg_num, ...)` and `send_msg(msg_num, ...)`, which attach `__FILE__` and `__LINE__`.
- `fsck_ref_msg(msg_num)` resolves a message ID to `msg_defs[msg_num].msg_txt`.

## Message Namespace
- Highest defined ID: `fsck_highest_msgid_defined` = 599.
- `0-399`: fsck status, validation, repair, parameter, superblock, inode, directory, block-map, bad-block, xchklog/xchkdmp, and insertion-token messages.
- `400-599`: logredo/recovery messages, including journal scan, map update, redo/no-redo page handling, and low-level read/write failures.
- Several aliases intentionally share numeric IDs for text insertions, e.g. `fsck_ACL`, `fsck_aggr_inode`, and `fsck_aggregate` map into the insertion-token range.

## Data Structures
- `struct fsck_message` contains `msg_num`, fixed text buffer `msg_txt[300]`, and `msg_level`.
- Constants define max log entry length, max message text length, max parameter length, and max parameter count.

## Notes
Uses GNU-style variadic macro syntax (`arg...`, `## arg`), so this header expects a compiler mode compatible with that extension. Undefined/reserved message slots are preserved for compatibility.
