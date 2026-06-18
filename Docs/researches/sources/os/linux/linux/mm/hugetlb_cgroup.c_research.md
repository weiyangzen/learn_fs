# File Research: sources/os/linux/linux/mm/hugetlb_cgroup.c

## Purpose

`hugetlb_cgroup.c` implements the HugeTLB cgroup controller. It tracks and limits HugeTLB usage per hstate for both fault-time page consumption and reservation-time commitments, exposes cgroup v1/v2 control files, records per-node usage for NUMA reporting, emits limit events, reparents charged pages on cgroup offline, and migrates cgroup ownership during HugeTLB folio migration.

## Major Responsibilities

- Allocate and initialize `struct hugetlb_cgroup` CSS objects with per-hstate usage and reservation `page_counter`s.
- Maintain separate counters for actual huge page usage (`hugepage[]`) and reserved huge page commitments (`rsvd_hugepage[]`).
- Charge, commit, uncharge, and migrate HugeTLB cgroup state for folios and reservation maps.
- Provide cgroup v2 files such as `<size>.max`, `<size>.current`, `<size>.rsvd.max`, `<size>.rsvd.current`, `<size>.events`, `<size>.events.local`, and `<size>.numa_stat`.
- Provide legacy cgroup v1 files such as `<size>.limit_in_bytes`, usage, max usage, failcnt, reservation equivalents, and numa stats.
- Track per-node usage in `h_cgroup->nodeinfo[nid]->usage[idx]` for NUMA stat output.
- Reparent charged active huge pages to the parent cgroup when a hugetlb cgroup goes offline.

## Cgroup Lifetime

`hugetlb_cgroup_css_alloc()` allocates a flex-array `hugetlb_cgroup`, allocates per-node `hugetlb_cgroup_per_node` structures, assigns the root cgroup, and initializes all counters through `hugetlb_cgroup_init()`. Each hstate gets usage and reserved counters with parent linkage. Legacy mode enables failcnt tracking. Limits are rounded down to huge-page multiples.

`hugetlb_cgroup_css_offline()` repeatedly scans every hstate active list under `hugetlb_lock` and calls `hugetlb_cgroup_move_parent()` until the cgroup has no usage. Actual charged folios are moved to the parent, or to the root cgroup if there is no parent. Reservation charges are not reparented because reservations hold their own CSS references.

## Charge and Uncharge Flow

The charge path uses `__hugetlb_cgroup_charge_cgroup()`. It obtains the current task's hugetlb cgroup under RCU, pins the CSS, and attempts a `page_counter_try_charge()` against either the usage or reserved counter. Limit failures increment the `HUGETLB_MAX` event. Non-reservation charges immediately drop the CSS reference because the folio pointer does not own a CSS reference; reservation charges keep it until reservation uncharge.

Commit helpers require `hugetlb_lock`:

- `hugetlb_cgroup_commit_charge()` records actual usage ownership on a folio and increments per-node usage.
- `hugetlb_cgroup_commit_charge_rsvd()` records reservation ownership on a folio.

Uncharge helpers clear folio cgroup pointers, uncharge the matching page counter, drop reserved CSS references when needed, and decrement per-node usage for actual charges. Reservation-only uncharge can also happen from a whole `resv_map`, a `file_region`, or a charged cgroup pointer when an allocation/reservation path aborts.

## User Interface

The file dynamically builds cftype arrays once hstates are known. `hugetlb_cgroup_cfttypes_init()` prefixes each template file with a formatted huge page size such as `2MB` or `1GB`, encodes the hstate index and resource attribute in `cftype.private`, adjusts event file offsets per hstate, and registers lockdep keys.

For cgroup v2, limits use `max` syntax and output `max` when the counter limit is the rounded page-counter maximum. For legacy cgroups, limits use `-1`, max/fail counters can be reset by writing, and failcnt tracking is enabled. All byte values are rounded down to the hstate page size before being stored as page-counter units.

`hugetlb_cgroup_read_numa_stat()` prints non-hierarchical node usage in legacy mode and hierarchical node totals by walking descendant CSS objects. `hugetlb_event()` increments local and hierarchical event counters and notifies cgroup files.

## Migration and Integration

`hugetlb_cgroup_migrate()` moves both actual and reserved cgroup pointers from an old folio to a new folio while holding `hugetlb_lock`, then moves the new folio onto the hstate active list. It is used by HugeTLB migration state transfer in `hugetlb.c`.

The file depends on `hugetlb_lock` to serialize folio cgroup pointer updates, active-list scans during cgroup offline, and migration against cgroup removal. It is tightly coupled with `hugetlb.c` reservation-map code through `resv_map`, `file_region`, and cgroup reservation uncharge metadata.
