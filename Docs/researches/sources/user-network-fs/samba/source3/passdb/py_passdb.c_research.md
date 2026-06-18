# sources/user-network-fs/samba/source3/passdb/py_passdb.c

## Purpose
`py_passdb.c` is the C Python extension for Samba's source3 password database APIs. It exposes `passdb.Samu`, `passdb.Groupmap`, and `passdb.PDB` Python types, plus module helpers for loading Samba configuration, selecting an alternate secrets directory, retrieving domain SIDs, and reinitializing the static passdb backend. The module is a thin but broad bridge from Python into `struct samu`, `GROUP_MAP`, `struct pdb_methods`, secrets, SID/GUID, idmap, account policy, alias, trust-domain, and LSA secret operations.

## Important APIs, types, and functions
- `PySamu` wraps `struct samu` and provides generated get/set properties for account timestamps, strings, SIDs, password hashes/history/plaintext password, account control flags, logon hours, counters, country code, and code page. Setters use the corresponding `pdb_set_*` functions with `PDB_CHANGED`.
- `PyGroupmap` wraps `GROUP_MAP` with properties for `gid`, `sid`, `sid_name_use`, `nt_name`, and `comment`.
- `PyPDB` wraps a `struct pdb_methods` backend instance created by `make_pdb_method_name(url)`.
- `py_pdb_methods` exposes account CRUD (`getsampwnam`, `getsampwsid`, `create_user`, `delete_user`, `add_sam_account`, `update_sam_account`, `rename_sam_account`), group mapping and membership APIs, alias APIs, account policy get/set, id/SID mapping, RID allocation, trusted-domain password APIs, full trusted-domain object APIs, and generic LSA secret get/set/delete.
- Module-level functions include `get_backends`, `set_smb_config`, `set_secrets_dir`, `reload_static_pdb`, `get_global_sam_sid`, and `get_domain_sid`.
- `MODULE_INIT_FUNC(passdb)` readies pytalloc-backed types, creates the module and `passdb.error`, registers the types, and imports `dom_sid`, `security.descriptor`, and `misc.GUID` Python type objects used for type checking and object construction.

## Control flow
Object creation is simple: `Samu()` allocates a new `struct samu`, `Groupmap()` allocates a zeroed `GROUP_MAP`, and `PDB(url)` loads a passdb backend by name. Most `PDB` methods parse Python arguments, obtain the wrapped `pdb_methods` pointer, call one backend method, and either return converted Python data or raise `passdb.error` with the NTSTATUS value and friendly message. Search/enumeration APIs use backend search iterators and convert entries into Python dictionaries/lists. SID and security descriptor arguments are accepted as pytalloc objects of imported Samba Python types. Trust and LSA secret methods marshal between Python dictionaries and Samba's `secrets.c`/`secrets_lsa.c` data structures.

For `Samu` and `Groupmap`, property accessors translate between Python scalar/string/bytes/SID objects and the underlying C structures. Password fields and logon hours are binary-sensitive paths; they copy bytes into passdb setters rather than treating all values as null-terminated text. Module-level setup functions mutate global Samba process state: `set_smb_config` loads global loadparm state, `set_secrets_dir` initializes `secrets.tdb` at an explicit private directory, and `reload_static_pdb` calls `initialize_password_db(true, NULL)`.

## State and persistence behavior
The Python objects are pytalloc wrappers around Samba C allocations, so lifetime depends on talloc ownership transferred to Python. Mutating a `Samu` property only changes the in-memory `struct samu`; persistence happens when callers pass it to `add_sam_account`, `update_sam_account`, or other backend methods. `PDB` operations persist through the selected passdb backend, which may be TDB, LDAP, DSDB, or another compiled backend. Trust-domain passwords and LSA secrets persist through `secrets.tdb`. Configuration and static passdb reload calls affect process-global Samba state and can change how later `PDB` objects and module helpers behave.

## Dependencies and integration points
This file depends on Python C API compatibility wrappers, pytalloc, source3 passdb APIs, `secrets.h`, idmap, Samba SID/security/GUID Python modules, loadparm, and generated NDR/RPC structures. It is built as `samba/samba3/passdb.so` by `wscript_build`. Python Samba tooling that needs legacy source3 account database operations imports this extension instead of reimplementing passdb logic.

## Risks and edge cases
- It exposes high-privilege account, password hash, trust password, and secret operations to Python; caller authorization and filesystem permissions around the selected backend and `secrets.tdb` are critical.
- Many methods pass through raw backend status. Python callers must handle `passdb.error`; otherwise partial account or group mutations can be left in place.
- The module mutates global loadparm/passdb/secrets state, so test suites or long-lived Python processes can affect subsequent operations by calling `set_smb_config`, `set_secrets_dir`, or `reload_static_pdb`.
- Type conversions rely on imported Samba Python type objects and pytalloc pointers. Incorrect type checks or lifetime mistakes can become C-level crashes rather than Python exceptions.
- Binary fields such as hashes, password history, logon hours, trust auth blobs, and LSA secret blobs must not be treated as UTF-8 text by callers.

## Test signals
Useful tests import `samba.samba3.passdb`, instantiate each exported type, verify all `Samu` and `Groupmap` properties round-trip, exercise `PDB("tdbsam")` or a test backend for account/group/alias CRUD, and use a temporary private directory to validate `set_secrets_dir`, trusted-domain password methods, and LSA secret get/set/delete. Build-time signals include successful compilation of the Python extension and import-time resolution of `samba.dcerpc.security.dom_sid`, `descriptor`, and `samba.dcerpc.misc.GUID`.
