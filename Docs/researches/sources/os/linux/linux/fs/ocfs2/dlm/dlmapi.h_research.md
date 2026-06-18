# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmapi.h

## Purpose
Defines the externally exported OCFS2 DLM API used by filesystem code and other DLM clients.

## Status Model
`enum dlm_status` defines DLM return/status codes, including:
- normal/granted/denied states
- blocked and async-working states
- resource and argument errors
- value-block validity errors
- recovery and migration extension statuses
- protocol/version and device-related errors.

`dlm_errname()` returns printable names, and `dlm_error()` logs most statuses while suppressing routine recovery/migration/forward statuses.

## Lock Status Block
`struct dlm_lockstatus` exposes:
- `status`
- `flags`
- opaque `lockid`
- 64-byte LVB buffer.

Callers are documented as only allowed to access `status` and `lvb`.

## Lock Modes
Defines DLM modes:
- invalid
- null
- concurrent read/write placeholders
- protected read
- protected write placeholder
- exclusive.

OCFS2 compatibility logic mainly supports NL, PR, and EX.

## Lock Flags
Defines public lock/unlock flags such as:
- `LKM_VALBLK`
- `LKM_NOQUEUE`
- `LKM_CONVERT`
- `LKM_UNLOCK`
- `LKM_CANCEL`
- `LKM_INVVALBLK`
- `LKM_FORCE`.

Also defines internal OCFS2 extensions:
- `LKM_MIGRATION`
- `LKM_PUT_LVB`
- `LKM_GET_LVB`
- `LKM_RECOVERY`.

## Callback Types
- `dlm_astlockfunc_t`: lock grant AST.
- `dlm_bastlockfunc_t`: blocking AST.
- `dlm_astunlockfunc_t`: unlock AST.

## Public Operations
- `dlmlock()`: request or convert a lock.
- `dlmunlock()`: unlock/cancel/deallocate lock.
- `dlm_register_domain()`: join/register a DLM domain with filesystem protocol version.
- `dlm_unregister_domain()`: leave/unregister domain.
- `dlm_print_one_lock()`: debug print a lock.
- eviction callback setup/register/unregister functions.

## Protocol Version Type
`struct dlm_protocol_version` stores major/minor protocol values for DLM/filesystem locking negotiation.
