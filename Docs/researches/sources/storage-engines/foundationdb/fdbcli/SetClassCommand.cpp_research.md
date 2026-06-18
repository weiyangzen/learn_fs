# sources/storage-engines/foundationdb/fdbcli/SetClassCommand.cpp

Purpose: Implements `setclass`, listing process classes or changing the class type for a registered process address.

Important APIs/types/functions: `setClassCommandActor`, private `printProcessClass`, `setProcessClass`, special ranges `processClassSourceSpecialKeyRange` and `processClassTypeSpecialKeyRange`, `getSpecialKeysFailureErrorMessage`, and `CommandFactory setClassFactory`.

Control flow: No arguments lists all registered process class types and sources by scanning both special-key ranges, asserting they align by size and address order. Two arguments look up the requested address under class type keys, reject if absent, set the class type value, and commit. Invalid arity prints usage.

State and persistence behavior: Process class type changes are persisted via special keys under `\xff\xff/configuration/process/class_type/`. Source metadata is read only. No local state.

Dependencies and integration points: Depends on fdbclient process-class configuration keys, special-key writes, and cluster recruitment/role assignment behavior that consumes process classes.

Risks: The list path assumes type/source ranges are sorted identically and have equal cardinality. Class type strings are not locally validated against the documented enum; invalid values are expected to be rejected by special-key API or downstream validation. Changing process classes can alter role recruitment and performance.

Test signals: Cover listing empty/non-empty process maps, mismatched source/type range detection, unknown address, valid class set, invalid class special-key error, retry behavior, and documented class names.
