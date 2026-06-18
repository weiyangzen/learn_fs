# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/authzone.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8713, source bytes 262124, report `Docs/researches/chunks/chunk_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_services_authzone_c_1__e93fdf9bc36e_research.md`
- chunk 2: lines 8714-8828, source bytes 2592, report `Docs/researches/chunks/chunk_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_services_authzone_c_2__675bbb0bf2bb_research.md`

## Chunk Research

### Chunk 1: lines 1-8713

# Chunk Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/authzone.c lines 1-8713

## Scope

This chunk covers almost all of `authzone.c`, the Unbound/OpenBSD unwind authoritative-zone implementation for locally hosted zones. It includes zone data storage, zonefile parsing/writing, answer generation, DNSSEC denial proof generation, RPZ integration hooks, NOTIFY handling, AXFR/IXFR/HTTP zone transfer state machines, ZONEMD hash/DNSSEC verification, and the start of memory accounting. The file continues after line 8713 with the remainder of memory accounting and worker task disowning.

## Main APIs Covered

- Zone container lifecycle and configuration: `auth_zones_create`, `auth_zones_delete`, `auth_zones_apply_cfg`, `auth_zones_cleanup`.
- Zone lookup/answering: `auth_zones_lookup`, `auth_zones_downstream_answer`, `auth_zones_can_fallback`.
- Zone object helpers: `auth_zone_create`, `auth_zone_find`, `auth_zones_find_zone`, `auth_zone_set_zonefile`, `auth_zone_set_fallback`, `auth_zone_read_zonefile`, `auth_zone_write_file`, `auth_zone_get_soa_rrset`, `auth_zone_get_serial`.
- Transfer lifecycle: `auth_xfer_create`, `auth_xfer_delete`, `auth_xfer_pickup_initial`, `auth_zones_notify`, `auth_zones_startprobesequence`, `xfer_set_masters`.
- Network/event callbacks exported to the rest of Unbound: `auth_xfer_transfer_lookup_callback`, `auth_xfer_transfer_timer_callback`, `auth_xfer_transfer_tcp_callback`, `auth_xfer_transfer_http_callback`, `auth_xfer_probe_timer_callback`, `auth_xfer_probe_udp_callback`, `auth_xfer_probe_lookup_callback`, `auth_xfer_timer`, `auth_zonemd_dnskey_lookup_callback`.
- ZONEMD/public helpers: `compare_serial`, `zonemd_hashalgo_supported`, `zonemd_scheme_supported`, `auth_zone_generate_zonemd_hash`, `auth_zone_generate_zonemd_check`, `auth_zone_verify_zonemd`, `auth_zones_pickup_zonemd_verify`.

## Core State

- `struct auth_zones` owns two rbtrees: `ztree` for `auth_zone` objects and `xtree` for `auth_xfer` transfer state. It also tracks downstream availability and an RPZ linked list protected by `rpz_lock`.
- `struct auth_zone` stores the zone name/class, an rbtree of `auth_data` domain nodes, config flags (`for_upstream`, `for_downstream`, `fallback_enabled`, `zonemd_check`, `zonemd_reject_absence`, `zone_expired`, `zone_is_slave`), optional `zonefile`, optional `rpz`, and online ZONEMD callback fields.
- `struct auth_data` represents one owner name and a sorted linked list of `auth_rrset`.
- `struct auth_rrset` stores one RR type and a `packed_rrset_data` blob. RRSIGs are usually stored inside the covered RRset; orphan signatures may remain in an RRSIG rrset.
- `struct auth_xfer` mirrors a zone’s identity and SOA lease state (`have_zone`, `serial`, `refresh`, `retry`, `expiry`, `lease_time`, `zone_expired`) plus three task structs: `task_nextprobe`, `task_probe`, and `task_transfer`.
- `struct auth_master` entries serve multiple roles: transfer masters, HTTP URLs, and allow-notify sources. Looked-up addresses are stored in `struct auth_addr` lists.
- `struct auth_chunk` stores downloaded or transferred packet/content fragments until the complete transfer can be parsed and atomically applied.

## Control Flow

### Zone Configuration And Loading

`auth_zones_apply_cfg` marks existing zones deleted, iterates `cfg->auths`, creates or reuses zones via `auth_zones_cfg`, removes still-deleted zones, reads zonefiles, and optionally initializes transfer SOA state. `auth_zones_cfg` is the central config merger: it creates `auth_zone`, creates `auth_xfer` when masters or URLs are configured, sets zone flags, initializes RPZ state, and fills probe/transfer master lists. RPZ locking is acquired before the normal zone lock to avoid dependency cycles.

`auth_zone_read_zonefile` handles chroot path adjustment, clears current zone data and RPZ policies, initializes parser state with default TTL 3600 and `$ORIGIN` as the zone name, then calls `az_parse_file`. `$INCLUDE` recursion is supported to `MAX_INCLUDE_DEPTH`. Each parsed wire RR is inserted through `az_insert_rr`.

### RR Storage Mutations

RR insert/delete paths normalize wire-format RRs into `packed_rrset_data`:

- `az_insert_rr` validates class, creates/fetches an owner node, and calls `az_domain_add_rr`.
- `az_domain_add_rr` handles duplicate suppression and RRSIG placement. RRSIGs are attached to the covered RRset when possible; otherwise they are held in an RRSIG rrset until the covered RRset appears.
- `rrset_add_rr`, `rrset_remove_rr`, `rrset_moveover_rrsigs`, and `rrsigs_copy_from_rrset_to_rrsigset` reallocate packed blobs to maintain Unbound’s packed rrset layout.
- `az_remove_rr` and `az_domain_remove_rr` remove RRs and delete empty owner nodes from the rbtree. RPZ insert/remove mirrors normal zone mutations when `z->rpz` exists.

Packet-originated transfer RRs are first decompressed by `decompress_rr_into_buffer`, because transfer packets may compress owner names and dnames inside rdata.

### Answer Generation

`auth_zones_lookup` is used for upstream/iterator access when the delegation point name is known. It locks `az`, finds the exact zone, then locks `z`; disabled or expired zones return fallback information.

`auth_zones_downstream_answer` serves incoming downstream queries. It searches for the best enclosing auth zone, special-cases DS by checking the parent delegation name, handles local aliases, verifies `for_downstream`, and encodes either a local authoritative answer or SERVFAIL/fallback.

`auth_zone_generate_answer` builds a `dns_msg` in a regional allocator, finds the owner node or closest match, runs `az_find_ce` to account for delegations, DNAMEs, NSEC3-only nodes, and closest enclosers, then dispatches to:

- Positive answers: `az_generate_positive_answer`, with A/AAAA additionals for MX/SRV/NS.
- CNAME chains: `az_generate_cname_answer` and `follow_cname_chain`, capped at `MAX_CNAME_CHAIN`.
- ANY: `az_generate_any_answer`, intentionally returns a small selected subset.
- NODATA: `az_generate_notype_answer`.
- Referrals: `az_generate_referral_answer`, clears AA and includes DS or denial proof.
- DNAME: `az_generate_dname_answer`, creates synthetic CNAME and may return YXDOMAIN on target overflow.
- Wildcards: `az_generate_wildcard_answer`, rewrites owner names in regional rrsets and adds wildcard denial proof.
- NXDOMAIN: `az_generate_nxdomain_answer`.

NSEC and NSEC3 helpers (`az_find_nsec_cover`, `az_nsec3_param`, `az_nsec3_hashname`, `az_nsec3_find_cover`, `az_add_nsec3_proof`) construct DNSSEC denial material. Negative SOA TTLs are adjusted to the SOA minimum in `az_add_negative_soa`.

### NOTIFY And Transfer Scheduling

NOTIFY enters through `auth_zones_notify`. The code finds the xfer by exact zone name/class, validates the sender against `allow_notify_list` using direct addresses, resolved address lists, or allowed netblocks, then calls `xfr_process_notify`.

`xfr_process_notify` compares the notify serial with local state via RFC1982-style `compare_serial`/`xfr_serial_means_update`. If the zone is stale, it starts a probe sequence; if probe/transfer is already active, it records the freshest pending notify serial.

The transfer state machine has three task layers:

- `task_nextprobe`: timer-driven lease/refresh/retry scheduling (`xfr_set_timeout`, `auth_xfer_timer`), including exponential failure backoff capped at `AUTH_TRANSFER_MAX_BACKOFF`.
- `task_probe`: optional hostname lookups, UDP SOA probes, retrying one target with increasing timeout from `AUTH_PROBE_TIMEOUT` to `AUTH_PROBE_TIMEOUT_STOP`, and deciding whether transfer is needed.
- `task_transfer`: hostname lookups, TCP IXFR/AXFR or HTTP fetch, chunk accumulation, transfer validation, and applying the complete result.

Task ownership is tied to `env->worker`; disown helpers delete timers/commpoints because another worker may later own a task on a different event base.

### Transfer Fetch And Apply

Transfer startup resolves hostnames through `mesh_new_callback`, then attempts each master/address. HTTP URLs use `outnet_comm_point_for_http`; DNS transfers use `outnet_comm_point_for_tcp` and `xfr_create_ixfr_packet`.

`check_xfer_packet` validates transfer packet headers, qname/qclass/qtype, answer/authority/additional RR structure, start/end SOA rules, IXFR up-to-date responses, IXFR-as-AXFR responses, and IXFR-to-AXFR fallback triggers. Valid packets are copied into `auth_chunk` nodes by `xfer_link_data`.

Once complete, `process_list_end_transfer` calls `xfr_process_chunk_list`, which reacquires `auth_zone` and `auth_xfer` locks in a controlled order and applies data:

- `apply_ixfr` iterates transferred answer RRs, toggles delete/add mode at SOA boundaries, verifies the second SOA starts at the current local serial, and soft-fails to AXFR if duplicate additions or nonexistent removals are observed.
- `apply_axfr` clears the whole zone/RPZ, inserts all RRs until the closing SOA, and updates xfer serial/have-zone.
- `apply_http` treats chunks as a zonefile, syntax-checks the first non-comment RR, handles `$ORIGIN` and `$TTL`, ignores includes, clears the zone/RPZ, and inserts parsed RRs line by line.

After a successful apply, `xfr_process_chunk_list` clears expiration flags, reads SOA timings, runs ZONEMD verification, finishes RPZ config, updates lease/acquisition time, optionally writes a temp zonefile and renames it over the configured zonefile, then resumes normal refresh scheduling. A ZONEMD failure marks both zone and transfer expired unless permissive mode is enabled.

### ZONEMD

The chunk implements both digest generation and policy verification:

- `zonemd_fetch_parameters` parses serial/scheme/hash algorithm/hash from ZONEMD rdata.
- `auth_zone_zonemd_check_hash` requires SOA serial match, rejects duplicate scheme/hash algorithm pairs, accepts unsupported schemes/algorithms as non-fatal unsupported results, and calls `auth_zone_generate_zonemd_check` for supported hashes.
- Only SIMPLE scheme, SHA384, and SHA512 are supported.
- `zonemd_simple_collate` walks the canonical `z->data` tree. `zonemd_simple_domain` sorts rrsets by type, canonicalizes each rrset, handles RRSIG collation specially, and omits apex ZONEMD and RRSIGs over apex ZONEMD as required.
- DNSSEC integration verifies SOA/ZONEMD signatures when a chain exists, or verifies NSEC/NSEC3 absence when ZONEMD is absent.
- `auth_zone_verify_zonemd` chooses trust-anchor verification, online DNSKEY/DS lookup, insecure handling, or absence handling depending on anchors and mode. Online lookups store `z->zonemd_callback_env` and are completed by `auth_zonemd_dnskey_lookup_callback`.

## Dependencies

- Unbound DNS data structures and encoders: `query_info`, `dns_msg`, `reply_info`, `ub_packed_rrset_key`, `packed_rrset_data`, `reply_info_answer_encode`, `error_encode`, `rrset_canonicalize_to_buffer`.
- Domain-name utilities: `dname_*`, `query_dname_compare`, packet name decompression/copy helpers.
- `sldns` parsing and wire helpers for zonefiles, RRs, DNS packets, rdata printing, and base32 NSEC3 hash owner names.
- Event/network substrate: `comm_point`, `comm_timer`, `outnet_comm_point_for_udp/tcp/http`, `mesh_new_callback`.
- Validator subsystem: trust anchors, DNSKEY/DS verification, NSEC/NSEC3 bitmap checks, signature verification, secure/insecure/bogus status.
- RPZ subsystem: `rpz_create`, `rpz_config`, `rpz_insert_rr`, `rpz_remove_rr`, `rpz_clear`, `rpz_finish_config`, `rpz_get_mem`.
- Concurrency primitives: `lock_rw_*`, `lock_basic_*`, and `lock_protect`.

## Risks And Edge Cases

- The file is lock-order sensitive. Several paths intentionally unlock `xfr` or `z` around callbacks or ZONEMD verification because callbacks may run immediately and because mesh lookups can re-enter state machines.
- Transfer apply is all-or-fail at the chunk-list level but mutates in-memory data while applying. IXFR soft failures can leave a temporarily modified zone and then force a full refetch; comments indicate this is accepted to keep serving “fairly nice” data during refetch.
- `az_empty_nonterminal` appears to advance with `rbtree_next(&node->node)` inside a loop even after assigning `next`; if `node` is not the same as `next`, this is a subtle area to audit for iterator correctness.
- Packed RRset mutation uses manual size arithmetic and pointer fixups. Incorrect `rdatalen`, `count`, or `rrsig_count` handling can corrupt packed layout.
- ZONEMD collation uses a stack array of 65,536 `auth_rrset*` entries in `zonemd_simple_domain`, which is large for stack usage.
- HTTP zone downloads parse text chunks manually for line collation, parentheses, comments, `$ORIGIN`, and `$TTL`; includes are deliberately ignored for downloaded zones.
- `parse_url` supports only HTTP/HTTPS and custom IPv6 bracket handling; malformed port strings are accepted through `strtol` without explicit range validation in this chunk.
- Expired zones behave differently depending on `fallback_enabled`, `for_upstream`, and downstream path. Upstream lookup can fallback; downstream may SERVFAIL if fallback is disabled.
- ZONEMD permissive mode logs but does not block failed zones; without it, failures set `zone_expired`.
- The chunk ends at line 8713 inside `auth_addrs_get_mem`; the rest of memory accounting and `xfr_disown_tasks` are outside this chunk and should be merged from the adjacent tail.

## Cross-Chunk References

- Continuation after line 8713 completes `auth_addrs_get_mem`, adds `auth_primaries_get_mem`, `auth_chunks_get_mem`, `auth_xfer_get_mem`, `az_ztree_get_mem`, `az_xtree_get_mem`, public `auth_zones_get_mem`, and `xfr_disown_tasks`.
- No earlier chunk exists for this file; this chunk starts at the file header and includes the forward declarations for the transfer state machine.
- The final per-file report should connect this chunk’s public APIs to declarations in `services/authzone.h` and to callers in iterator/downstream/worker code outside this file.

### Chunk 2: lines 8714-8828

# Chunk Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/authzone.c lines 8714-8828

## Scope

This chunk covers the tail of `auth_addrs_get_mem()`, the complete memory-accounting helpers for authoritative-zone transfer state, the public `auth_zones_get_mem()` entry point, and `xfr_disown_tasks()` for worker-specific task release. It is within the `sources/os/bsd/openbsd-src` source tree included by `Docs/research_subset_a.md`.

The range starts inside `auth_addrs_get_mem()`; the function signature and local initialization are immediately before the chunk. The range ends at the end of `xfr_disown_tasks()`.

## APIs and Entry Points

- `auth_primaries_get_mem(struct auth_master *list)` sums one linked list of upstream/notify masters, including each `struct auth_master`, resolved `auth_addr` entries via `auth_addrs_get_mem()`, and optional `host`/`file` strings.
- `auth_chunks_get_mem(struct auth_chunk *list)` sums buffered transfer chunks as `sizeof(*chunk) + chunk->len` for each linked node.
- `auth_xfer_get_mem(struct auth_xfer *xfr)` is the internal accumulator for one zone transfer object, including the `auth_xfer` object, zone name storage, task timers/comm points, transfer chunks, configured master lists, and `allow_notify_list`.
- `auth_zones_get_mem(struct auth_zones *zones)` is the exported memory-usage API declared in `authzone.h`; it returns zero for `NULL`, otherwise accounts the shared auth-zone container and both zone and transfer rbtrees.
- `xfr_disown_tasks(struct auth_xfer *xfr, struct worker *worker)` is the exported worker-lifecycle helper declared in `authzone.h`; it releases any next-probe, probe, or transfer task currently owned by the given worker.

## Control Flow

Memory accounting is a set of straight-line tree/list walks. `auth_primaries_get_mem()` iterates `auth_master->next`, recursively counts `auth_master->list` address nodes, and conditionally adds C-string storage. `auth_chunks_get_mem()` iterates `auth_chunk->next` and adds each payload allocation length.

`auth_xfer_get_mem()` assumes a valid, fully initialized `auth_xfer`: it dereferences `task_nextprobe`, `task_probe`, and `task_transfer` unconditionally. It counts timer memory for next-probe, probe and transfer master lists, probe and transfer comm points/timers, transfer chunk buffers, and the allow-notify master list.

`auth_zones_get_mem()` establishes the top-level lock order by taking `zones->rpz_lock` for reading, then `zones->lock` for reading. It walks `ztree` with `az_ztree_get_mem()`, which takes each zone's read lock while calling `auth_zone_get_mem()`, and walks `xtree` with `az_xtree_get_mem()`, which takes each transfer's basic lock while calling `auth_xfer_get_mem()`. Locks are released in reverse order.

`xfr_disown_tasks()` checks each task's `worker` pointer against the supplied `worker`. Matching tasks are passed to `xfr_nextprobe_disown()`, `xfr_probe_disown()`, or `xfr_transfer_disown()`. Those helpers delete task-local event objects and clear ownership/env fields.

## State and Data Flow

- Shared container state: `struct auth_zones` owns `ztree`, `xtree`, `lock`, and `rpz_lock`; this chunk reports aggregate memory for that container and the nodes below both trees.
- Zone state: `az_ztree_get_mem()` relies on `auth_zone_get_mem()` from the previous lines, which accounts zone name storage, optional zonefile string, auth data tree, and optional RPZ state.
- Transfer state: `auth_xfer_get_mem()` reads `xfr->namelen`, `task_nextprobe->timer`, `task_probe->{masters,cp,timer}`, `task_transfer->{chunks_first,masters,cp,timer}`, and `allow_notify_list`.
- Master/address state: `auth_primaries_get_mem()` counts configured or copied master lists plus resolved address lists, but only by allocation shape visible in `struct auth_master` and `struct auth_addr`.
- Worker task ownership: `xfr_disown_tasks()` uses `task_*->worker` identity to decide which event resources belong to the worker being detached.

## Dependencies

This chunk depends on local auth-zone structures from `authzone.h`: `auth_zones`, `auth_zone`, `auth_xfer`, `auth_nextprobe`, `auth_probe`, `auth_transfer`, `auth_master`, `auth_addr`, and `auth_chunk`.

It also depends on local helpers defined earlier in `authzone.c`: `auth_zone_get_mem()`, `auth_addrs_get_mem()` prologue, `xfr_nextprobe_disown()`, `xfr_probe_disown()`, and `xfr_transfer_disown()`. Event memory accounting is delegated to libunbound comm helpers `comm_timer_get_mem()` and `comm_point_get_mem()`. Tree traversal and synchronization use `RBTREE_FOR`, `lock_rw_rdlock()`, `lock_rw_unlock()`, `lock_basic_lock()`, and `lock_basic_unlock()`.

## Risks and Edge Cases

- `auth_xfer_get_mem()` unconditionally dereferences all three task pointers and their timer/comm fields. It relies on construction invariants that these task objects exist even if their worker-owned event handles are `NULL`.
- `auth_zones_get_mem()` reports an approximate live allocation total while holding read locks; it does not include allocator overhead and depends on each helper matching the ownership model of its structures.
- `auth_chunks_get_mem()` adds `chunk->len` rather than inspecting `chunk->data`; this is correct only if `len` is the allocated payload length, as documented in `authzone.h`.
- `xfr_disown_tasks()` does not take `xfr->lock` itself. The disown helpers' comments state their caller must hold `xfr.lock`, so callers of this exported helper must preserve that locking contract.
- `xfr_disown_tasks()` does not delete transfer chunks before disowning a transfer task. Nearby `auth_zones_cleanup()` deletes chunks before `xfr_transfer_disown()`, so callers must decide whether buffered transfer data should be retained or freed.
- The disown path assumes `task_nextprobe`, `task_probe`, and `task_transfer` are non-NULL before checking their `worker` fields.

## Cross-Chunk References

- The beginning of `auth_addrs_get_mem()` and the full `auth_zone_get_mem()` implementation are immediately before this chunk.
- Earlier chunks define the auth-zone data-tree memory helpers used by `auth_zone_get_mem()`.
- Earlier transfer code defines `xfr_nextprobe_disown()`, `xfr_probe_disown()`, and `xfr_transfer_disown()`; those helpers delete timers/comm points and clear task ownership.
- Earlier lifecycle code such as `auth_zones_cleanup()` shows the same disown helpers used while holding `xfr->lock`, and also shows that transfer chunks may need explicit deletion before transfer-task disowning.
- `authzone.h` declares the exported APIs `auth_zones_get_mem()` and `xfr_disown_tasks()` and documents the task ownership model: task `worker == NULL` means unowned, and worker-owned event resources live on that worker's event base.
