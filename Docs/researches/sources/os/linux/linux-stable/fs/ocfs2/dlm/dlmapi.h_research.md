# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmapi.h

## Summary
Defines the external OCFS2 DLM API used by filesystem locking code and related clients. It contains DLM status values, lock status blocks, supported lock modes and flags, callback types, lock/unlock entry points, domain registration, lock printing, and eviction callback registration.

## Main Responsibilities
- Define `enum dlm_status` and declare `dlm_errname()` for readable status reporting.
- Provide `dlm_error()` logging wrapper for noteworthy DLM status failures.
- Define lock status block flags and `struct dlm_lockstatus`.
- Define DLM lock modes, including OCFS2-supported NL, PR, and EX modes.
- Define public and internal lock/unlock flags.
- Define AST, BAST, and unlock-AST callback function types.
- Declare `dlmlock()` and `dlmunlock()`.
- Declare domain registration/unregistration and protocol-version negotiation input.
- Define DLM eviction callback registration helpers.

## Key Interfaces
- `dlmlock()` requests or converts a lock with callbacks and caller data.
- `dlmunlock()` unlocks/cancels/deallocates a lock and optionally runs an unlock AST.
- `dlm_register_domain()` joins or creates a DLM domain using a domain name, key, and filesystem locking protocol version.
- `dlm_unregister_domain()` leaves/releases a DLM domain.
- `dlm_setup_eviction_cb()`, `dlm_register_eviction_cb()`, and `dlm_unregister_eviction_cb()` manage callbacks for node eviction events.

## Important Behavior
The status enum includes both traditional DLM results and OCFS2 extensions such as `DLM_RECOVERING` and `DLM_MIGRATING`, allowing callers to treat lock-resource recovery or migration as special retry/fail cases. `DLM_MAXSTATS` is the upper validation bound.

Only selected lock modes are supported by OCFS2 in practice: null, protected-read, and exclusive. Several flags are marked unsupported, while internal extension flags (`LKM_MIGRATION`, `LKM_PUT_LVB`, `LKM_GET_LVB`, `LKM_RECOVERY`) are reserved for DLM internals.

The lock status block is intentionally limited for callers: comments say callers are only allowed to access `status` and `lvb`, although the struct also carries flags and the internal lock id.

## State and Synchronization
This header defines callback-driven asynchronous completion rather than state itself. Callers supply AST/BAST functions that the DLM may invoke while holding spinlocks, as documented in `dlmcommon.h` for the lock structure.

## Cross-File Interactions
The implementation is spread across the DLM object members in the Makefile. `dlmcommon.h` includes and extends this API with internal state, wire messages, and helper prototypes. OCFS2 `dlmglue` and filesystem lock code use these declarations.

## Risks
Status and flag values form ABI-like contracts between DLM components and network peers. Changing the enum requires synchronizing debug/status-name code, as noted in the file. Callers must not use unsupported flags or modes unless the internal DLM path explicitly owns them. LVB get/put flags are subtle because stale value-block propagation can corrupt lock metadata semantics.
