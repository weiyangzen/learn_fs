# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/schema_util.c

Purpose: `schema_util.c` provides utility functions for reading, writing, and updating the serialized `schemaInfo` attribute on the schema partition. It is not itself an LDB module; it is a helper used by schema-changing modules such as `samldb.c`.

Important APIs, types, and functions: Public helpers are `dsdb_module_schema_info_blob_read()`, `dsdb_module_schema_info_blob_write()`, and `dsdb_module_schema_info_update()`. Internal helpers `dsdb_schema_info_write_prepare()`, `dsdb_module_schema_info_read()`, and `dsdb_module_schema_info_write()` convert between LDB messages, NDR blobs, and `struct dsdb_schema_info`.

Control flow: Read locates the schema base DN, searches for `schemaInfo`, and transfers the blob into the caller's memory context. Write builds a replace modify message for `schemaInfo` and sends it through `dsdb_module_modify()`. Update obtains the local NTDS invocation ID, reads the existing schemaInfo or creates a default when missing, increments the revision, sets the invocation ID, and writes the updated blob back.

State and persistence behavior: The durable state is the `schemaInfo` attribute on the schema root. The helper deliberately does not update the in-memory `schema->schema_info` after writing because the surrounding transaction may still fail and because the schema object may be shared globally. The next schema reload observes the stored value.

Dependencies and integration points: It depends on DSDB common utilities, NDR DRS blob helpers, LDB module search/modify wrappers, and `samdb_ntds_invocation_id()`. `samldb_schema_info_update()` calls `dsdb_module_schema_info_update()` when classSchema or attributeSchema entries are added by originating writes.

Risks: Incorrect memory ownership around blobs could leave dangling data, so the read helper steals blob data into the caller's context. The update path must be called within a transaction by callers, otherwise schemaInfo could advance without the associated schema change. Error handling maps missing schemaInfo to a default only for update, while malformed blobs become operational errors.

Test signals: Schema extension tests should verify that schemaInfo revision and invocation ID change on originating schema updates, but not on replicated/provisioning paths that bypass updates. Tests should also cover missing initial schemaInfo and failed schemaInfo decoding.
