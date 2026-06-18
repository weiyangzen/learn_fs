# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/objectguid.c

## Purpose
`objectguid.c` adds immutable identity and update metadata to directory objects. On add it generates `objectGUID`, `whenCreated`, `whenChanged`, `uSNCreated`, and `uSNChanged` when needed. On modify it updates `whenChanged` and `uSNChanged` while rejecting attempts to alter `objectGUID`.

## Important APIs, types, and functions
Helpers `add_time_element()` and `add_uint64_element()` append timestamp and uint64 attributes only when absent, using replace flags that are ignored for adds. `objectguid_add()` and `objectguid_modify()` are the operation handlers. `struct og_context` stores module/request pointers for child request ownership. Registration is through `ldb_objectguid_module_init()`.

## Control flow
Special DNs bypass the module. Add rejects any caller-specified `objectGUID` with `LDB_ERR_UNWILLING_TO_PERFORM`, shallow-copies the message, generates `GUID_random()`, adds it with `dsdb_msg_add_guid()`, fills created/changed timestamps from `time(NULL)`, asks the backend for `LDB_SEQ_NEXT`, and fills USN attributes if the sequence call succeeds. It then builds and sends a child add request.

Modify rejects `objectGUID` changes with `LDB_ERR_CONSTRAINT_VIOLATION`, copies the modify message, appends `whenChanged`, obtains the next sequence number when available, appends `uSNChanged`, and sends a child modify request.

## State and persistence behavior
The module has no private durable state but writes durable metadata attributes into add/modify requests. It depends on the backend sequence counter for USNs; if sequence retrieval fails, the operation still proceeds without adding USN fields.

## Dependencies and integration points
It integrates with DSDB message helpers, LDB sequence numbers, time formatting, and downstream replication metadata expectations. Other modules rely on `objectGUID` existing, especially extended-DN output/store and linked-attribute GUID resolution.

## Risks and edge cases
Proceeding when `ldb_sequence_number()` fails may create objects or modifications lacking USN metadata in backends that do not support sequences. The module only rejects explicit `objectGUID`; caller-supplied timestamp/USN values are preserved because helpers skip existing attributes. That may be intentional for provisioning/replication but is worth testing in untrusted paths.

## Test signals
Test add generation, add rejection with explicit `objectGUID`, modify rejection with explicit `objectGUID`, timestamp/USN defaulting, preservation of caller-supplied timestamp/USN fields, behavior when sequence numbers are unsupported, and downstream modules resolving newly generated GUIDs.
