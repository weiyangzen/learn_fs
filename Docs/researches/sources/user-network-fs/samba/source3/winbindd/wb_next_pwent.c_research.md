# sources/user-network-fs/samba/source3/winbindd/wb_next_pwent.c

Purpose: drives one step of `getpwent` enumeration across winbind domains, filling the next passwd entry for a domain user.

Important APIs and types: `wb_next_pwent_send/recv`; `struct wb_next_pwent_state`; shared `struct getpwent_state` containing current domain ref, RID list, and next index.

Control flow: `wb_next_pwent_send_do` resolves the current domain ref. When the current RID list is exhausted it frees it, advances to the next domain, and calls `dcerpc_wbint_QueryUserRidList_send`. Otherwise it composes a user SID from the domain SID plus current RID and calls `wb_getpwsid_send`. The RID-list callback ignores per-domain query errors, resets `next_user`, and recurses. The fill callback skips `NT_STATUS_NO_SUCH_USER` entries, otherwise propagates errors or completes after incrementing the cursor.

State and persistence: cursor state lives in the caller-owned `getpwent_state`. The request owns only the composed SID and pointer to caller-provided `winbindd_pw`.

Dependencies and integration points: child `QueryUserRidList`, `wb_getpwsid`, domain iteration, `winbindd_domain_ref`, and NSS enumeration request handlers.

Risks: per-domain RID-list errors are swallowed to allow enumeration to continue, which can hide partial outages. `wb_getpwsid` failures other than `NO_SUCH_USER` abort enumeration. The caller-provided `winbindd_pw` is mutated in place.

Test signals: RID list fetch success/failure, users without UID mapping skipped as `NO_SUCH_USER`, transition between domains, stale domain ref, and final `NO_MORE_ENTRIES`.
