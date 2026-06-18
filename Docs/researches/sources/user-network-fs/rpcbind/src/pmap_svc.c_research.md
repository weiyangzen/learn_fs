# sources/user-network-fs/rpcbind/src/pmap_svc.c

## Purpose
Implements the legacy version 2 portmapper service interface when `PORTMAP` is enabled.

## APIs, Flow, And State
`pmap_service` dispatches PMAP NULL, SET, UNSET, GETPORT, DUMP, and CALLIT. `find_service_pmap` finds exact or same-program mappings from `list_pml`. `pmapproc_change` decodes `struct pmap`, derives owner from local uid or superuser checks, authorizes, maps protocol to netid, constructs IPv4/IPv6 wildcard universal addresses for SET, calls `map_set`, or unsets TCP and UDP mappings. `pmapproc_getport` authorizes, finds a mapping, validates it with `is_bound`, deletes dead programs, sends the port, and updates stats. `pmapproc_dump` returns `list_pml`. Protocol conversion helpers map TCP/UDP netids and IP protocol numbers.

## Dependencies And Integration
Depends on libtirpc pmap/rpcb XDR, global rpcbind lists, `check_access`, `map_set`, `map_unset`, `delete_prog`, `rpcbs_*` stats, and remote-call common code.

## Risks And Test Signals
Compatibility with legacy PMAP clients is the central risk. Address construction is limited to TCP/UDP wildcard addresses, and stale binding checks depend on `check_bound.c`. Tests should exercise authorization, set/unset/getport/dump, protocol conversion, dead-service deletion, and stats updates.
