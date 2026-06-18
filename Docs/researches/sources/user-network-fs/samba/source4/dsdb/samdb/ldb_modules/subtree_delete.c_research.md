# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/subtree_delete.c

Purpose: `subtree_delete.c` implements the `subtree_delete` LDB module. It prevents accidental deletion of non-leaf entries unless the tree-delete control is present, and recursively deletes children before the requested parent when tree delete is authorized.

Important APIs, types, and functions: The main handler is `subtree_delete()`, registered as the module `del` hook. `subtree_delete_init()` registers `LDB_CONTROL_TREE_DELETE_OID` with rootDSE. The module uses `dsdb_module_search()` to detect one-level children and `dsdb_module_del()` for recursive child deletion.

Control flow: Special DNs are passed through. For normal deletes, the module searches one level below the target. If there are no children, the request passes downstream unchanged. If children exist and the request lacks `LDB_CONTROL_TREE_DELETE_OID`, it returns `LDB_ERR_NOT_ALLOWED_ON_NON_LEAF`. With the control present, it deletes each child through the top module with AS_SYSTEM, TRUSTED, and DSDB_TREE_DELETE flags, preserving relax semantics when requested, then lets the original delete continue.

State and persistence behavior: The module stores no state. Persistence is the recursive sequence of downstream deletes. Children are deleted first because parent deletion happens only after recursive child calls complete and the original request reaches lower modules.

Dependencies and integration points: It relies on upstream ACL checks for delete-tree rights and then uses `DSDB_FLAG_AS_SYSTEM` because authorization is considered complete. It interacts with modules such as objectclass and samldb by starting recursive deletes at the top module so normal constraints still apply.

Risks: Recursive deletion order and flags are security-sensitive. Failing to start from the top module could bypass constraints; failing to pass trusted/system flags could cause authorized tree deletes to fail mid-tree. Error strings intentionally avoid DN output because older MMC clients mishandle some subtree delete errors.

Test signals: Tests should cover deleting leaves, rejecting non-leaf deletes without control, deleting nested subtrees with control, relax-control propagation, and failures from child constraints. Integration tests are more valuable than unit tests because behavior depends on module stack ordering.
