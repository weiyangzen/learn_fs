# sources/user-network-fs/samba/source3/winbindd/winbindd_cred_cache.c

## Purpose

`winbindd_cred_cache.c` manages process-local Kerberos credential-cache entries and mlocked memory credentials. It refreshes Kerberos tickets, regains tickets after offline authentication, and stores password/hash material needed by cached NTLM and Kerberos rekinit paths.

## Important APIs, Types, and Functions

- `MAX_CCACHES`, `ccache_list`, and `memory_creds_list` bound and hold live entries.
- Ccache APIs: `add_ccache_to_list()`, `remove_ccache()`, `ccache_entry_exists()`, `ccache_entry_identical()`, `ccache_regain_all_now()`, `ccache_remove_all_after_fork()`.
- Timer handlers: `krb5_ticket_refresh_handler()`, `krb5_ticket_gain_handler()`, and `add_krb5_ticket_gain_handler_event()`.
- Memory credential APIs: `find_memory_creds_by_name()`, `winbindd_add_memory_creds()`, `winbindd_delete_memory_creds()`, `winbindd_replace_memory_creds()`.
- Private memory helpers allocate, `mlock()`, hash, zero, and `munlock()` credential buffers.

## Control Flow

`add_ccache_to_list()` validates parameters, enforces `MAX_CCACHES`, reuses identical entries by increasing refcount, or allocates a new ccache entry. If ticket refresh is enabled and the ticket is renewable, it schedules either a refresh timer at half the remaining lifetime or a gain timer for postponed/offline requests. Entries with refresh timers also store memory credentials for future rekinit.

`krb5_ticket_refresh_handler()` renews tickets as the target UID. If renewal is no longer possible, it tries password-based rekinit. KDC/realm reachability failures destroy maybe-stale tickets but schedule later gain attempts. `krb5_ticket_gain_handler()` waits for the domain to be online and then performs password-based kinit, scheduling normal refresh on success.

Memory credentials are one contiguous block containing NT hash, LM hash, and optional plaintext password. Existing entries are refcounted and replaced on add; delete decrements and zeroes/unlocks on final removal.

## State and Persistence Behavior

The lists and timers are process-local. Kerberos ccaches named by `entry->ccname` are external and are destroyed on final removal. Memory credentials are intended to be protected with `mlock()` where available. `ccache_remove_all_after_fork()` removes inherited entries and timers after fork.

## Dependencies and Integration Points

The file integrates with Samba Kerberos helpers, tevent global context, effective UID switching, winbind domain lookup/online state, configuration (`winbind refresh tickets`, `winbind cache time`), `winbindd_ccache_access.c`, and `winbindd_cm.c` via `ccache_regain_all_now()` on domain-online transitions.

## Risks and Edge Cases

Plaintext passwords are intentionally retained for rekinit. Platforms without `mlock`/`munlock` compile no-op memory storage paths that report success but do not create usable buffers. Refcount imbalances can leak or prematurely destroy tickets. Timer callbacks must always regain root privilege after user-UID Kerberos calls. Misconfigured realms can create repeated retry timers.

## Test Signals

Test ccache creation/reuse/mismatch, max limit, removal and `ads_kdestroy()`, fork cleanup, timer scheduling, offline gain retry, rekinit after expired renewal, mlock failure, memory credential add/replace/delete refcounting, and clearing ccache `cred_ptr` on memory-credential deletion.
