# sources/user-network-fs/samba/source4/param/provision.c

Purpose: `provision.c` is C glue that calls Samba Python provisioning/schema code from C callers and bridges Python objects back to C `loadparm_context` and `ldb_context` pointers.

Important APIs, types, and functions: Key functions are `dict_insert`, `provision_module`, `schema_module`, `ldb_module`, `PyLdb_FromLdbContext`, `call_wrapper`, `provision_bare`, `py_dom_sid_FromSid`, `provision_store_self_join`, and `provision_get_schema`.

Control flow: Each public function initializes Python, updates `sys.path`, imports the target module, builds a kwargs dict, calls the Python function with no positional arguments, and extracts result attributes. `provision_bare` calls `samba.provision.provision_become_dc`. `provision_store_self_join` opens `secrets.ldb`, starts a transaction, passes an LDB wrapper to `secretsdb_self_join`, then commits. `provision_get_schema` calls `samba.schema.ldb_with_schema` and returns the embedded LDB.

State and persistence behavior: Provisioning changes are performed by Python code and LDB/secrets transactions. The C layer persists self-join changes only if the LDB transaction commits. Returned `samdb`, schema LDB, and loadparm contexts are talloc-referenced into the caller's memory context.

Dependencies and integration points: It depends on Python C API, pyldb, pytalloc, Samba Python modules, dynconfig path setup, secrets database helpers, NDR SID wrappers, and loadparm bridge utilities.

Risks: Reference ownership is delicate around borrowed module dictionaries and Python attributes. Error handling often returns generic `NT_STATUS_UNSUCCESSFUL` after printing Python errors. A failed path after starting a transaction must cancel or free correctly. Python module availability is runtime-critical.

Test signals: Tests should cover successful bare provision and self-join, Python import failure, transaction commit failure, schema override prefixmap, returned LDB/loadparm lifetime, and error string propagation.
