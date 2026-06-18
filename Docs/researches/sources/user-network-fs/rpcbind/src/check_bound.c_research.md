# sources/user-network-fs/rpcbind/src/check_bound.c

## Purpose
Tracks transports used by rpcbind and provides address-bound checks, merged universal-address generation, and netconfig lookup by netid.

## APIs, Flow, And State
Static `fdlist` nodes form a linked list of netconfigs. `add_bndlist` clones a netconfig entry and appends it. `check_bound` converts a universal address to a transport address, opens a socket for that netconfig, and attempts bind; success means the service is not currently bound, while bind failure means it is bound. In this version `check_binding` is set false, so checks currently return true. `is_bound` finds the matching netid and delegates. `mergeaddr` validates binding, derives the caller universal address from either supplied `saddr` or `SVCXPRT`, and calls `addrmerge`. `rpcbind_get_conf` returns the stored netconfig.

## Dependencies And Integration
Uses libtirpc netconfig/address conversion and rpcbind helpers such as `addrmerge`. Service lookup paths in pmap/rpcb call `is_bound`, `mergeaddr`, and `rpcbind_get_conf`.

## Risks And Test Signals
Disabled bound checking means stale registrations may persist unless other paths delete them. When enabled, bind-as-probe semantics are subtle and treat conversion/socket errors as bound. Test signal would include service death cleanup, merged address correctness, and netid lookup behavior.
