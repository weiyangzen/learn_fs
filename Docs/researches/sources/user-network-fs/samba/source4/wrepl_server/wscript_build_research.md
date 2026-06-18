# sources/user-network-fs/samba/source4/wrepl_server/wscript_build

Source read signal: reviewed complete local file (11 lines, 417 bytes).

## Purpose
This Waf build fragment defines Samba's private `WREPL_SRV` subsystem for the `source4/wrepl_server` directory. It gathers the WINS replication server implementation files into one internal library-like component.

## Important APIs, types, and functions
The only build API is `bld.SAMBA_SUBSYSTEM('WREPL_SRV', ...)`. The source list includes `wrepl_server.c`, inbound connection/call handling, outbound helper/pull/push code, record application, periodic processing, and scavenging. Public dependency declarations include `LIBCLI_WREPL`, `WINSDB`, `process_model`, `DCERPC_COMMON`, `LIBCLI_RESOLVE`, `LIBCLI_NBT`, `samba-hostconfig`, `ldb`, and `events`.

## Control flow
There is no runtime control flow. During configure/build, Waf uses this fragment to compile the listed C files and link the resulting subsystem into higher-level Samba service modules.

## State and persistence
The file has no runtime state. Its persistent effect is build graph state: the exact object list and dependency set that make WREPL server code available.

## Dependencies and integration points
It integrates with the parent `source4/wscript_build`, which references `WREPL_SRV` from `service_wrepl`. It also declares the protocol, database, process model, resolver, NBT, hostconfig, LDB, and event dependencies the source files need.

## Risks
The source list must stay synchronized with generated prototypes and service module references. Missing a new source file can produce unresolved symbols; keeping a removed source can break builds. Dependency under-declaration can hide until non-unified or minimal builds.

## Test signals
Run the Samba Waf build for the `service_wrepl` module or all of source4. Link errors around WREPL symbols and missing headers are the key signals.
