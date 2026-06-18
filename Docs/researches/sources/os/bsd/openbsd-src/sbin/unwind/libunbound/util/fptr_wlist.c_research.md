# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/fptr_wlist.c

## Role

`fptr_wlist.c` implements function-pointer whitelist checks for Unbound. Each exported `fptr_whitelist_*` function verifies that an indirect callback pointer equals one of the known legitimate functions for that callback category.

## Whitelist Categories

The file covers communication callbacks, raw communication callbacks, timers, signals, accept start/stop hooks, libevent-style event callbacks, pending UDP/TCP callbacks, serviced-query callbacks, rbtree comparators, lruhash size/compare/delete/mark-delete callbacks, module environment callbacks, module lifecycle callbacks, alloc cleanup, tube listeners, mesh callbacks, print/collation callbacks, in-place reply/query/EDNS/query-response callbacks, and serve-expired lookup callbacks.

The allowed functions span core Unbound modules and optional build features: worker/libworker, outside network, mesh, iterator, validator, DNS64, response-IP, auth zones, local zones, infra/rrset/key/rate caches, remote control, Windows service hooks, Python module, dynamic library module, cachedb, ipsecmod, ECS/subnet, ipset, dnstap, and DNS-over-QUIC support where enabled.

## Security and Build Configuration

Most whitelist functions are straightforward pointer equality chains. Optional module callbacks are guarded by compile-time feature macros such as `WITH_PYTHONMODULE`, `WITH_DYNLIBMODULE`, `USE_CACHEDB`, `USE_IPSECMOD`, `CLIENT_SUBNET`, `USE_IPSET`, `USE_DNSTAP`, `HAVE_NGTCP2`, and `UB_ON_WINDOWS`.

For exported-all-symbols or disabled-feature cases, unused parameters are explicitly cast to void. The file intentionally violates normal modular boundaries because its purpose is to centralize every allowed indirect-call target.

## Research Notes

This is a control-flow hardening file. Any new callback target introduced elsewhere in the resolver must be added to the correct whitelist or `fptr_ok()` checks will reject it. Conversely, overly broad additions here weaken the indirect-call integrity model.
