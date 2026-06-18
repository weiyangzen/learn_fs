# sources/user-network-fs/samba/source4/dsdb/tests/python/dsdb_schema_info.py

Purpose: this schema regression test verifies that Samba updates the `schemaInfo` blob revision and invocation ID correctly when schema attributes or classes are added and renamed.

Important APIs/types/functions: `SchemaInfoTestCase` keeps a static `sam_db` connection. `_getSchemaInfo()` reads `schemaInfo` from the schema DN, unpacks it as `schemaInfoBlob`, and synthesizes revision 0 if absent. `_checkSchemaInfo()` expects revision increment and invocation ID stability. `_ldap_schemaUpdateNow()` triggers schema reload. `_make_attr_ldif()` and `_make_class_ldif()` generate schema LDIF with random OID suffixes. Tests are `test_AddModifyAttribute()`, `test_AddModifyClass()`, and `test_AddModifyClassLocalRelaxed()`.

Control flow: setup connects to `ldap://$DC_SERVER`, reads rootDSE for schema/base/forest details, and records the local invocation ID. Tests snapshot schemaInfo, add a schema object, call schemaUpdateNow, verify revision increment, rename the object, and verify again. The relaxed local test reconnects to `lp.samdb_url()` and passes `relax:0`.

State and persistence behavior: tests add and rename schema objects permanently; there is no deletion cleanup. The static connection persists across test methods, except the relaxed test overwrites `self.sam_db` with a local connection.

Dependencies and integration points: depends on environment variables described in the header, Samba test connection helpers, `schemaInfoBlob` NDR decoding, DRSUAPI/misc GUID support, schema update controls, and local/remote SamDB behavior.

Risks: schema changes are persistent and globally visible. Random OID suffixes reduce collisions but do not remove test artifacts. `_checkSchemaInfo()` always compares against the original pre-change blob in each test, so after a second schema modification it still expects `before + 1`, which may hide or expose revision semantics depending on server behavior.

Test signals: valid `schemaInfo` length/marker, revision increment, unchanged invocation ID equal to the DC invocation ID, and successful schema object rename.
