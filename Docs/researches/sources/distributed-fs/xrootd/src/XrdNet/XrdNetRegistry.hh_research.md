# sources/distributed-fs/xrootd/src/XrdNet/XrdNetRegistry.hh

## Purpose
`XrdNetRegistry.hh` declares the pseudo-host registry interface used to map `%`-prefixed names to concrete network contacts.

## Important APIs, Types, and Functions
`pfx` is the required `%` prefix. `GetAddrs()` expands a registered name into `XrdNetAddr` values and reports ordering partition info. Two `Register()` overloads accept either an array of host strings or a comma-separated string, with optional error text and rotation.

## Control Flow and State
The API is static, process-wide, and stateful. Successful registration makes later `XrdNetUtils::GetAddrs()` calls able to resolve pseudo-hosts.

## Dependencies and Integration Points
It includes `XrdNetUtils.hh` for `AddrOpts` and forward-declares `XrdNetAddr`. It is part of the address-resolution layer, not a standalone service.

## Risks and Test Signals
Callers must include ports in registered targets and must not expect unregister/delete support. Tests should verify error text for invalid arguments and integration through `XrdNetUtils`.
