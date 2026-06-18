# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/instancetype.c

## Purpose
`instancetype.c` enforces and defaults the Active Directory `instanceType` attribute. On add, it validates caller-specified values or adds `INSTANCE_TYPE_WRITE` when missing. On modify, it rejects changes to `instanceType` except when dbcheck is repairing data.

## Important APIs, types, and functions
The module has two operation handlers: `instancetype_add()` and `instancetype_mod()`. It uses `INSTANCE_TYPE_IS_NC_HEAD`, `INSTANCE_TYPE_WRITE`, and `INSTANCE_TYPE_UNINSTANT` from DS common flags, plus `DSDB_CONTROL_PARTIAL_REPLICA` and `DSDB_CONTROL_DBCHECK`. It builds rewritten add requests with `ldb_build_add_req()` and `samdb_msg_add_uint()`.

## Control flow
Special DNs bypass all logic. On add, if `instanceType` exists, the module requires exactly one value. Non-NC values may only be `0` or include `INSTANCE_TYPE_WRITE`. NC-head adds must include `WRITE`, except partial replica creation must include `UNINSTANT`. Valid supplied values pass through unchanged. If the attribute is absent, the module shallow-copies the message, adds `instanceType: INSTANCE_TYPE_WRITE`, builds a new add request, and sends it to the next module.

On modify, any `instanceType` element causes `LDB_ERR_CONSTRAINT_VIOLATION` unless `DSDB_CONTROL_DBCHECK` is present; otherwise the request passes through.

## State and persistence behavior
This module writes no private state. Its persistence impact is adding `instanceType` on new objects and preventing ordinary later changes. The added value is part of the downstream add request.

## Dependencies and integration points
It integrates with `new_partition.c` and `objectclass.c`, which also inspect `INSTANCE_TYPE_IS_NC_HEAD` for naming-context creation. Dbcheck can bypass the modify protection to repair inconsistent records.

## Risks and edge cases
The TODO notes that the default instance type is not fully calculated; it always uses `INSTANCE_TYPE_WRITE` for ordinary adds. Partial replica validation is narrow and depends on the presence of `DSDB_CONTROL_PARTIAL_REPLICA`. Misordered modules could cause `new_partition` or objectclass logic to see missing/defaulted values differently.

## Test signals
Test adds with no `instanceType`, valid and invalid non-NC values, NC-head values with and without `WRITE`, partial replica values with and without `UNINSTANT`, multi-valued `instanceType`, ordinary modify rejection, and dbcheck modify allowance.
