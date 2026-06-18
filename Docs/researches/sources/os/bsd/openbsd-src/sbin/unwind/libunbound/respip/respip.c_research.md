# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/respip/respip.c

Implements Unbound’s response-IP module, which inspects A/AAAA answers and applies configured actions when returned addresses match configured netblocks or RPZ response-IP triggers.

Data structures:
- `struct respip_addr_info`: copied matched address/netblock data for inform logging.
- `enum respip_state`: module state for initial processing and CNAME-subquery completion.
- `struct respip_qstate`: per-query response-IP state.

Configuration and storage:
- `respip_set_create()` builds a regional allocator, address tree, and rw lock.
- `respip_sockaddr_find_or_create()` and `respip_find_or_create()` manage address-tree nodes.
- Config application handles response-address tags, response-IP actions, and response-IP redirect data.
- Supports global response-IP config and per-view response-IP config.
- `respip_enter_rr()` validates redirect RR type against address family, rejects incompatible CNAME coexistence, creates rrsets, and inserts RDATA.
- `respip_copy_rrset()` deep-copies rrsets into a region, excludes RRSIGs, and normalizes memory layout.

Reply matching and rewriting:
- `respip_addr_lookup()` scans answer-section A/AAAA rrsets, validates RDATA length, converts addresses to sockaddr, and finds matching netblocks.
- `respip_rewrite_reply()` selects applicable action from view-specific data, global tag/action data, or RPZ zones.
- Tag-based redirect data can override configured node data.
- Actions can redirect, inform, deny/drop, refuse, synthesize NXDOMAIN/NODATA, pass through, or apply RPZ override behavior.
- Deny variants can mark `qstate->is_drop` so no response is sent.
- Redirect-to-CNAME actions can generate subqueries to complete the CNAME chain.

RPZ integration:
- Iterates auth-zone RPZ linked list under locks.
- Applies RPZ action overrides, CNAME override data, logging settings, disabled/pass-through behavior, and per-RPZ tags.
- Tracks `rpz_passthru` to stop later RPZ processing.

Module lifecycle:
- `respip_get_funcblock()` returns the module function block.
- `respip_operate()` passes new queries to the next module, rewrites final replies on module completion, and waits for subqueries when redirect CNAME completion is needed.
- `respip_inform_super()` merges CNAME target replies back into the original rewritten response.
- `respip_clear()` drops per-query module state.

CNAME handling:
- `generate_cname_request()` attaches a subquery for the redirect CNAME target.
- `respip_merge_cname()` appends target answer rrsets to the base reply, excluding RRSIGs from copied target rrsets and rejecting target replies that would themselves trigger response-IP action.

Logging/memory:
- `respip_inform_print()` emits inform/RPZ log lines with source address, matched response-IP netblock, action, qname, type, and class.
- `respip_set_get_mem()` reports set memory under read lock.
- `respip_set_swap_tree()` swaps prebuilt tree/region/tag metadata for updates.

Filesystem/storage relevance:
- No filesystem logic. Relevant as DNS response policy/cache-adjacent code with regional allocation, rbtrees, rw locks, per-view policy, and RPZ/auth-zone integration.
