# File Research: sources/os/linux/linux/block/sed-opal.c

## Summary
Implements the Linux block-layer TCG OPAL self-encrypting drive command engine and ioctl backend.

## Main Responsibilities
- Discovers OPAL feature support and COMID.
- Builds OPAL tokenized command buffers.
- Parses OPAL responses and method status codes.
- Starts and ends AdminSP/LockingSP sessions.
- Manages SID/Admin/User authentication, passwords, and keyring fallback.
- Configures locking ranges, shadow MBR, single-user mode, and table I/O.
- Handles secure erase, revert, PSID revert, stack reset, and suspend unlock replay.
- Dispatches `IOC_OPAL_*` ioctls behind `CAP_SYS_ADMIN`.

## Key APIs
- `init_opal_dev()`, `free_opal_dev()`.
- `sed_ioctl()`.
- `opal_unlock_from_suspend()`.
- Internal command sequencer: `execute_steps()`, `opal_send_recv()`, `cmd_start()`, `cmd_finalize()`.

## Important Behavior
`init_opal_dev()` allocates DMA-safe command/response buffers, initializes locking state, and runs discovery. Discovery parses feature descriptors, records COMID, geometry, locking flags, MBR state, and single-user-mode support.

Commands are encoded as OPAL atoms into a fixed 2048-byte buffer. The builder tracks `dev->pos` and uses `can_add()` to prevent overrun. `cmd_finalize()` closes the parameter list, appends method status scaffolding, pads to 4 bytes, and fills OPAL packet lengths and session numbers.

Responses are parsed into up to `MAX_TOKS` token descriptors pointing into the response buffer. Status extraction expects the OPAL method-status list near the end of the response, with special handling for `OPAL_ENDOFSESSION`.

High-level operations are arrays of `opal_step`, usually discovery, session start, one or more method calls, and session end. On failures after a session starts, `execute_steps()` attempts to terminate the session.

## Key Management
The file creates a built-in `.sed_opal` keyring at late init, optionally seeds it from `sed_read_key()`, and updates it when passwords change. Runtime keys can be supplied directly or read from the keyring through `opal_get_key()`.

## User-Facing Operations
`sed_ioctl()` supports saving unlock keys, lock/unlock, ownership, LSP activation/reactivation/revert, user activation, password changes, locking range setup/status, shadow MBR control, erase/secure erase, table read/write, discovery export, geometry/status queries, SUM status, and stack reset.

## State and Synchronization
Each `opal_dev` has a `dev_lock` covering command buffers, session state, previous response data, and saved suspend unlock list. Saved unlock entries are replayed by `opal_unlock_from_suspend()` and cleared on successful TPer revert or device free.

## Risks
This code is security-sensitive: it handles credentials, copies user buffers, and issues destructive drive commands. Correctness depends on fixed buffer accounting, OPAL token parsing bounds, session cleanup on errors, and careful synchronization around saved keys and command buffers.
