# File Research: sources/os/bsd/freebsd-src/sys/sys/vmmeter.h

Virtual memory and system activity counter header.

Key responsibilities:
- Defines `MAXSLP`, used by userland and scheduler logic for sleep-state interpretation.
- Defines `struct vmtotal`, the aggregate VM/run/sleep/swap state summary.
- Under kernel or `_WANT_VMMETER`, defines cache-line-aligned `struct vmmeter` with counter(9)-backed activity counters for context switches, traps, syscalls, interrupts, VM faults, pager activity, reactivation, page daemon work, frees, fork activity, and wired/no-free counts, followed by constant page distribution thresholds and page size/count values.
- Defines `VM_METER_NCOUNTERS` as the counter field count before `v_page_size`.
- Under `_KERNEL`, declares global `vm_cnt`, memory-pressure domainsets, counter add/inc/fetch macros, user wire count, wire/no-free helpers, free count, and low-memory threshold predicates for severe/minimum pressure globally, per-domain, or domain-set masked.

Dependencies:
- Uses counter(9), domainset, cache-line alignment, and VM page accounting globals.

Notable risks:
- The split between counter fields and constant fields is encoded by `VM_METER_NCOUNTERS`; inserting fields before `v_page_size` changes counter initialization/iteration expectations.
- Low-memory predicates are used at user/kernel boundaries and in pageout decisions, so domainset state must reflect current VM pressure accurately.
