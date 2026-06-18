# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/util.h

## Purpose
`util.h` declares the DSDB LDB module helper interface and module-specific request flags used by the implementation in `util.c` and related helper sources.

## Important APIs, Types, and Functions
It forward-declares DSDB, security, NETLOGON, and extended-operation types; defines `enum system_control_strip_critical`; includes generated `util_proto.h`; and exposes flag constants `DSDB_FLAG_NEXT_MODULE`, `DSDB_FLAG_OWN_MODULE`, `DSDB_FLAG_TOP_MODULE`, `DSDB_FLAG_TRUSTED`, `DSDB_FLAG_REPLICATED_UPDATE`, and `DSDB_FLAG_FORCE_ALLOW_VALIDATED_DNS_HOSTNAME_SPN_WRITE`.

## Control Flow and Behavior
The header does not implement control flow. Its flags drive the dispatch and control-attachment branches in the helper implementation, selecting whether a helper re-enters the next module, top-level LDB stack, or current module operation and whether the resulting request is trusted or replication-related.

## State and Persistence Behavior
There is no runtime state. The persistent behavioral contract is ABI/API level: many LDB modules compile against these declarations and generated prototypes.

## Dependencies and Integration Points
It pulls in generated NDR misc/security types, DSDB common utilities, NETLOGON definitions, and the generated `dsdb/samdb/ldb_modules/util_proto.h`. It is included by DSDB module sources that need common request wrappers or policy helpers.

## Risks and Edge Cases
The high-bit flag values must not collide with common DSDB request flags consumed by `dsdb_request_add_controls`. Any signature drift in `util_proto.h` affects many modules. Callers must pass one of next, top, or own flags where helper implementations require an explicit dispatch target.

## Test Signals
Compile tests across DSDB modules are the main signal. Behavioral tests should verify that each flag maps to the intended request path and that added flags continue to be recognized by `dsdb_request_add_controls` or module helper code.
