# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/damap_impl.h

Private implementation header for Delta Address Map. It defines the concrete map structure, per-address soft state, state flags, bitset membership tests, report types, and kstat counters used to implement stabilized address reporting.

Key elements:
- Includes DDI, time, devctl, nvpair, sysevent, bitset, and SDT headers needed by the implementation.
- Defines internal callback typedefs corresponding to the public activation/deactivation and configure/unconfigure callbacks.
- `struct dam` stores map name, flags, options, report mode, stabilization ticks, map size/highest ID, timeout ID, activation/config callback arguments and function pointers, address-to-ID hash, active/stable/report bitsets, per-address soft state, update/stable timestamps, stabilization counters, sync CV/lock, kstats, and sync timeout count.
- Map flags track stable-pending, destroy-pending, and full-set-add pending state.
- `dam_da_t` stores per-address flags, jitter/rereport count, reference count, provider/config private pointers, stable and reported nvlists, stabilization deadline, timestamps/counters, and address string pointer for debugging.
- Per-address flags track initialized, failed configuration, and released addresses.
- Report types distinguish address add and delete reports.
- Macros test whether an ID is in the report set or active/stable set.
- `dam_kstats` exposes cycles, overrun, jitter, and active-address counters.

Dependencies:
- Includes public `damap.h` indirectly through callback types and deactivation reasons, plus DDI string-ID hashing and bitsets.
- Used only by DAMAP implementation code and debugging/observability paths.

Research notes:
- The implementation maintains separate active, stable, and reported sets, which is what enables debounce and full-set reconciliation.
- Address soft state carries both current stable nvlist and newly reported nvlist, allowing configuration only after a report stabilizes.
- Timeout-driven stabilization and sync waiting are coordinated through `dam_lock`, `dam_sync_cv`, and timeout IDs.
