# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_msg.h

## Purpose

Provides message/logging support declarations for the `emlxs` driver. It includes the message catalog, defines per-source-file numeric identifiers, standard logging macros, and the in-memory circular message log structures.

## Main Definitions

- Includes `emlxs_messages.h` to expose the actual catalog declarations/definitions.
- `EMLXS_MSG_DEF(_number)` creates a static `_FILENO_` value for source files.
- File id constants map driver C files to numeric ids, including clock, diag, download, ELS, FCP, HBA, mailbox, memory, node, packet, Solaris, message, IP, thread, DFC, DHCHAP, FCT, dump, SLI3, SLI4, event, and FCF modules.
- `EMLXS_CONTEXT` expands to `port, _FILENO_, __LINE__`.
- `EMLXS_MSGF` maps to `emlxs_msg_printf`.
- `EMLXS_DEBUGF` maps to `emlxs_msg_printf` only when `EMLXS_DBG` is defined; otherwise it expands empty.
- `MAX_LOG_INFO_LENGTH` is `96`.

## Structures

`emlxs_msg_entry_t` records one log entry:

- entry id
- timestamp and high-resolution timestamp
- message pointer
- VPI, adapter instance, file number, and line number
- fixed additional-info buffer

`emlxs_msg_log_t` is the circular log:

- lock
- start time and instance
- size/count/next indices
- repeat counter
- pointer to entry buffer

## Integration Notes

This header ties message catalog entries to runtime logging. Source files likely call `EMLXS_MSG_DEF()` once, then use `EMLXS_CONTEXT` when logging.

## Risks and Gotchas

- `EMLXS_DEBUGF` expands to nothing in non-debug builds, so arguments in debug-only calls must not be required for side effects.
- The fixed 96-byte entry buffer truncates additional info unless callers handle formatting limits.
- `_FILENO_` is a static const per translation unit; duplicate ids are possible if new source files are added without updating this list.
