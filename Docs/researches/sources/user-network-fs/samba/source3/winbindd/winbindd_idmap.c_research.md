# sources/user-network-fs/samba/source3/winbindd/winbindd_idmap.c

## Purpose
Owns parent-side setup for the dedicated idmap child and builds a cached map from idmap configuration ranges to domain names/SIDs. This lets parent code split SID/Unix-ID mapping work by idmap domain before using the idmap child binding.

## Important APIs, Types, And Control Flow
`init_idmap_child()` allocates `static_idmap_child` and starts `wb_parent_idmap_setup_send()` as an optimization. `idmap_child()`, `is_idmap_child()`, `idmap_child_pid()`, and `idmap_child_handle()` expose the singleton child; the handle asserts setup produced at least one domain. `wb_parent_idmap_setup_send/recv()` serializes setup through `static_parent_idmap_config.queue`. The first waiter creates a default passdb domain entry for `get_global_sam_name()`, scans `idmap config DOMAIN : range` values with `lp_scan_idmap_domains()`, then resolves each non-wildcard domain name to a domain SID via `wb_lookupname_send()`. On completion it calls `setup_child(NULL, static_idmap_child, "log.winbindd", "idmap")` and marks the config initialized.

## State And Persistence
Maintains process-global `static_idmap_child` and `static_parent_idmap_config` with domain ranges, names, SIDs, queue, and initialized flag. No disk persistence; values derive from smb.conf and name lookups.

## Dependencies And Integration Points
Integrates with idmap config parsing, domain name lookup, child setup in `winbindd_dual.c`, global event context, passdb lookup flags, and callers that require `idmap_child_handle()`.

## Risks And Test Signals
Risks include stale config after smb.conf reload, ignored malformed ranges, wildcard domain SID omission, setup failure cleanup, and queue lifetime subtleties where the queue subrequest is held until recv. Test multiple concurrent setup callers, invalid ranges, low>high ranges, duplicate domains, wildcard config, lookup failures, reload behavior, and idmap child startup.
