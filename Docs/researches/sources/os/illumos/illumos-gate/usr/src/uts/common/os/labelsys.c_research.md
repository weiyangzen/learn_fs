# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/labelsys.c

## Purpose

`labelsys.c` implements the kernel side of several Trusted Solaris / Trusted Extensions labeling system calls and backing caches. It manages trusted network remote-host templates, remote-host cache entries, multilevel port lists, and the `labelsys()` syscall dispatcher.

This file is security-sensitive because it maps network peers and ports to label policy, enforces privilege checks for Trusted Network Database updates, and exposes label lookup operations used by the labeled networking stack.

## Main Interfaces

System call entry point:

- `labelsys()`

Trusted network remote host cache/template operations:

- `tcache_init()`
- `tnrh_load()`
- `find_rhc()`
- `find_tpc()`
- internal syscall handlers `tnrh()` and `tnrhtp()`

Multilevel port operations:

- `tsol_mlp_anon()`
- `tsol_next_port()`
- `tsol_mlp_port_type()`
- `tsol_mlp_findzone()`
- internal syscall handler `tnmlp()`

Debug helper:

- `tsol_print_label()`

## Trusted Host Database

The file keeps trusted network host templates in `tpc_name_hash`, keyed by template name and protected by `tpc_lock`. Template records are reference-counted through `TPC_HOLD` / `TPC_RELE` and invalidated rather than mutated in place. `tnrhtp_create()` replaces an existing template by marking the old one invalid, removing it from the hash, and inserting a newly allocated copy.

Remote host entries are stored in prefix-length-indexed hash tables:

- `tnrhc_table` for IPv4 prefixes `0..32`
- `tnrhc_table_v6` for IPv6 prefixes `0..128`

Lookup uses longest-prefix match in `find_rhc()`, walking from most-specific to least-specific prefix. IPv4-mapped IPv6 addresses are normalized to IPv4. Entries are reference-counted and protected by per-bucket locks. Hash tables are allocated lazily by prefix length with `tnrhc_init_table()`.

If a remote-host entry points to an invalidated template, `find_rhc()` may refresh the host entry by finding the replacement template and reloading the hash entry. If stale entries are not allowed and no replacement exists, the lookup fails.

## Initialization

`tcache_init()` initializes template and remote-host structures, asserts label initialization has already run, creates prefix-zero tables for IPv4 and IPv6, creates an internal `_unlab` template, and installs default `0.0.0.0/0` and `::/0` remote-host entries pointing to `_unlab`.

The internal `_unlab` template represents unlabeled hosts with default/admin-low label, admin-low minimum, admin-high maximum, and the default DOI.

## Remote Host Syscall Behavior

`tnrh()` handles:

- `TNDB_LOAD`: copy in a `tsol_rhent_t`, validate template name termination, find the named template, allocate a new remote-host cache entry, and install it.
- `TNDB_DELETE`: remove the matching host entry from its prefix table.
- `TNDB_GET`: perform lookup and copy the resolved template name back.
- `TNDB_FLUSH`: invalidate and release all remote-host entries.

Non-GET operations require `secpolicy_net_config(CRED(), B_FALSE)`.

## Template Syscall Behavior

`tnrhtp()` handles:

- `TNDB_LOAD`: validate host type and create/replace a template.
- `TNDB_GET`: look up a held template and copy its contents to userland.
- `TNDB_DELETE`: invalidate and remove the named template.
- `TNDB_FLUSH`: invalidate and clear all templates.

Template names are explicitly checked for NUL termination within `TNTNAMSIZ`.

## Multilevel Ports

Multilevel ports are tracked in ordered doubly linked lists of `tsol_mlp_entry_t` protected by reader/writer locks. There is one global shared-address list, `shared_mlps`, and each zone has a private `zone_mlps` list.

`mlp_add_del()` maintains sorted order by port and protocol and rejects overlapping ranges for the same protocol. Deletion requires an exact port-range match.

`tnmlp()` supports loading, getting the next matching entry, deleting, and flushing MLP entries. It selects either the shared list or a zone-local list based on `TSOL_MEF_SHARED`.

Runtime helpers classify ports:

- `tsol_mlp_port_type()` determines whether a port is private, shared, both, or single-level.
- `tsol_mlp_findzone()` maps a shared MLP packet port to the owning zone.
- `tsol_next_port()` skips over configured MLP ranges when choosing a single-level port.

## Concurrency And Lifetime

Important locks and invariants:

- `tpc_lock` protects the template hash.
- `tnrhc_g_lock` protects lazy allocation of prefix hash tables.
- Per-prefix-bucket `tnrh_lock` protects remote-host linked lists.
- Per-entry `rhc_lock` and `tpc_lock` fields coordinate refcount destruction.
- MLP lists use `mlpl_rwlock`.
- Templates and remote-host entries are invalidated before release so new lookups do not attach to deleting objects.

## Dependencies

Depends on Trusted Extensions label/network headers, IP address helpers, zones, policy checks, `mod_hash`, kernel memory allocation, copyin/copyout, DTrace probes, and label functions such as `getlabel()` and `fgetlabel()`.

## Research Notes

Key audit areas are longest-prefix match correctness, stale-template refresh behavior, deletion while lookups hold references, MLP range overlap logic, zone/shared MLP interactions, and privilege enforcement on all mutating Trusted Network Database operations.
