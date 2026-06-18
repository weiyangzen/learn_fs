# sources/user-network-fs/rpcbind/src/rpcb_stat.c

## Purpose
Maintains in-memory rpcbind statistics returned by the version 4 GETSTAT procedure.

## APIs, Flow, And State
Static `rpcb_stat_byvers inf` stores procedure counts, set/unset counts, address lookup counts, and remote-call counts by rpcbind version index. `rpcbs_procinfo` increments per-procedure counters after validating version/procedure bounds. `rpcbs_set` and `rpcbs_unset` count successful mapping changes. `rpcbs_getaddr` finds or creates an address-list record keyed by program/version/netid and increments success or failure based on returned universal address. `rpcbs_rmtcall` similarly records remote-call success/failure and indirect counts. `rpcbproc_getstat` returns `&inf`.

## Dependencies And Integration
Called by pmap/rpcb service dispatch and common remote-call/address lookup code. Uses `rpcbind_get_conf` for stable netid pointers.

## Risks And Test Signals
State is process-local and not synchronized, so multithreaded dispatch would need external serialization. Allocation failures silently drop new rows. The guard conditions for version indices are important because service code passes version-stat constants. Test signal should verify counters for success/failure paths and GETSTAT output shape.
