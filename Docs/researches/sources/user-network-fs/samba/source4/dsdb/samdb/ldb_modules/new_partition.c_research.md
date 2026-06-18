# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/new_partition.c

## Purpose
`new_partition.c` intercepts adds of naming-context heads and asks the partitions module to create the corresponding `@PARTITIONS` metadata before allowing the original add. It prevents duplicate partition entries by checking whether the target DN already exists.

## Important APIs, types, and functions
`struct np_context` tracks the module, original add request, existence-check search request, and extended partition-add request. `new_partition_add()` is the operation handler. `np_part_search_callback()` handles the nonexistence check and builds `DSDB_EXTENDED_CREATE_PARTITION_OID`. `np_part_mod_callback()` treats successful partition metadata update, or attribute/value-exists during metadata update, as permission to continue with the original add.

## Control flow
Special DNs bypass the module. For ordinary adds, the module only acts when `instanceType` exists and includes `INSTANCE_TYPE_IS_NC_HEAD`; non-NC adds pass through. Deleted partition objects are skipped. For NC-head adds, it builds a base search for the new DN with no attributes. If the search succeeds, the object already exists and the module returns `LDB_ERR_ENTRY_ALREADY_EXISTS`. If the search returns `LDB_ERR_NO_SUCH_OBJECT` and the final reply is done, it builds an extended operation containing `struct dsdb_create_partition_exop` with `new_dn`.

If the original add had `DSDB_CONTROL_PARTIAL_REPLICA`, the extended operation gets `DSDB_MODIFY_PARTIAL_REPLICA`. After the extended op completes, `np_part_mod_callback()` runs the original add.

## State and persistence behavior
The module itself has no durable private state. Its side effect is triggering partition metadata creation through the partitions module before the actual NC-head object is added. The original add persists only after metadata handling succeeds or reports an already-existing metadata value.

## Dependencies and integration points
It depends on `instanceType` semantics, DSDB extended operation `DSDB_EXTENDED_CREATE_PARTITION_OID`, `DSDB_CONTROL_PARTIAL_REPLICA`, and downstream partition module behavior. It coordinates with `instancetype.c` and `objectclass.c`, which also validate NC-head additions.

## Risks and edge cases
If module ordering means `instanceType` has not been added yet, this module will not detect a partition add. The existence search treats any success as duplicate object, which is intentional but makes exact lower-layer error mapping important. Deleted NC-head objects are skipped to avoid recreating deleted partition metadata during replication or repair.

## Test signals
Test ordinary adds, NC-head adds, duplicate target DN, deleted NC-head skip, partial replica control propagation, extended operation failure propagation, `LDB_ERR_ATTRIBUTE_OR_VALUE_EXISTS` tolerance in metadata update, and ordering with `instancetype`.
