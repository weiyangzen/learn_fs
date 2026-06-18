# sources/user-network-fs/samba/source4/wscript_build

Source read signal: reviewed complete local file (18 lines, 596 bytes).

## Purpose
This parent Samba4 Waf fragment wires top-level source4 server modules and subsystem directories into the build. For this research item its relevant role is including the WREPL server subdirectory and declaring the `service_wrepl` server module.

## Important APIs, types, and functions
It calls `bld.RECURSE()` for many source4 subdirectories including `wrepl_server`, and defines `bld.SAMBA_MODULE('service_wrepl', ...)` with `subsystem='service'`, `source='wrepl_server/service_wrepl.c'`, `deps='WREPL_SRV process_model'`, and `internal_module=False`. This exposes WREPL through Samba's service subsystem.

## Control flow
There is no runtime flow. Build-time flow recurses into component directories, then creates service modules such as LDAP, CLDAP, web, KDC, DNS, winbind, NBT, WREPL, KCC, DNS update, DNS query, RODC, and DREPL.

## State and persistence
The build graph is the only state. The `service_wrepl` declaration persists the relationship between the service loader and the private `WREPL_SRV` subsystem.

## Dependencies and integration points
The file is consumed by Samba's Waf build and service module registration. WREPL depends on the recursively built `wrepl_server` subsystem plus `process_model`.

## Risks
Removing the `wrepl_server` recursion or changing the `service_wrepl` dependency breaks WINS replication service availability even if the C files compile in isolation. Service module naming must match runtime registration expectations.

## Test signals
Build source4 and verify the `service_wrepl` module links. Runtime startup of Samba configured as a WINS server should reach `server_service_wrepl_init()`.
