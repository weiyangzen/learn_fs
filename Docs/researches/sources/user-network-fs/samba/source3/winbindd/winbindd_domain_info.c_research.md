# sources/user-network-fs/samba/source3/winbindd/winbindd_domain_info.c

## Purpose
Implements the async `WINBINDD_DOMAIN_INFO` external command. It resolves a requested domain name without forcing full initialization, ensures the domain is initialized when necessary, and returns the domain's canonical name, alternate DNS name, SID, AD/native flags, and primary-domain flag.

## Important APIs, Types, And Control Flow
`struct winbindd_domain_info_state` holds a `winbindd_domain_ref` plus ping input/output fields. `winbindd_domain_info_send()` finds the domain with `find_domain_from_name_noinit()`, stores a stable domain ref, and completes immediately for already initialized domains. For uninitialized domains it sends `dcerpc_wbint_Ping_send()` through `dom_child_handle(domain)`; the callback `winbindd_domain_info_done()` checks both transport status and wbint result, revalidates the domain ref, and verifies that the ping caused initialization. `winbindd_domain_info_recv()` copies fields into `response->data.domain_info`.

## State And Persistence
State is temporary tevent/talloc request state. The only persistent mutation is indirect: pinging the domain child can initialize `struct winbindd_domain` fields and child/DC connection state. No file or database output is written here.

## Dependencies And Integration Points
Depends on `winbindd.h`, `string_wrappers.h`, global event context helpers, generated `ndr_winbind_c.h`, domain refs, `dom_child_handle()`, and the in-child `_wbint_Ping` implementation.

## Risks And Test Signals
Risks include stale domain refs while an async ping is outstanding, child ping success that still leaves `domain->initialized` false, and truncated fixed-size response strings. Test by querying initialized and uninitialized domains, unknown domains, killed domain children during ping, and verifying returned SID/alt-name/AD/primary fields.
