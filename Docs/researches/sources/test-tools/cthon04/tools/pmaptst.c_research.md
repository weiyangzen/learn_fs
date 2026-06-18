# sources/test-tools/cthon04/tools/pmaptst.c

## Purpose
tests local portmapper registration by adding and removing a dummy program/version for UDP and TCP and showing `rpcinfo -p` before and after.

## Important APIs, Types, and Functions
`main()` uses `pmap_set()`, `pmap_unset()`, constants `PROG`, `VERS`, `UPORT`, `TPORT`, and shell command `rpcinfo -p`.

## Control Flow and State
It prints baseline rpcinfo, registers UDP mapping, prints, registers TCP mapping, prints, unregisters the program/version, prints again, and exits with the number of registration failures.

## Persistence and Dependencies
persistent state is temporary portmapper registrations until `pmap_unset()` succeeds. Dependencies: SunRPC portmap APIs, `rpcinfo`, shell, and a running local portmapper/rpcbind.

## Integration Points, Risks, and Test Signals
Integration is portmapper sanity testing. Risks include modifying global rpcbind state, fixed program number collisions, dependence on external `rpcinfo`, and permissions. Signals are visible mappings after set and removal after unset.
