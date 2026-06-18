# sources/test-tools/pynfs/nfs4.1/server41tests/st_xattr.py

Purpose: NFSv4.2 extended-attribute tests for support advertisement, get/set/remove/list behavior, create/replace/either semantics, and missing/existing attribute errors.

Important APIs/types/functions: `testGetXattrAttribute`, `testGetMissingAttr`, `testCreateNewAttr`, `testCreateNewIfMissingAttr`, `testUpdateOfMissingAttr`, `testExclusiveCreateAttr`, `testUpdateExistingAttr`, `testRemoveNonExistingAttr`, `testRemoveExistingAttr`, `testListNoAttrs`, and `testListAttrs`.

Control flow: tests create a file with `open_create_file_op`, close it with a module-level `current_stateid`, then operate on `user.attr*` names via `GETXATTR`, `SETXATTR`, `REMOVEXATTR`, and `LISTXATTRS`. Value tests read back bytes and compare exact values; list tests compare returned names and EOF.

State and persistence behavior: creates files and mutates their xattr namespace. The suite checks missing, create-only, replace-only, either, remove, and list states for user attributes.

Dependencies/integration: requires NFS minor version 2 or later (`VERS: 2-`), generated xattr constants, `FATTR4_XATTR_SUPPORT`, and server filesystem xattr support.

Risks and test signals: test docstrings have minor typos such as `NFS4_ON`, but assertions use actual status checks. It does not test list pagination beyond a large enough 8192-byte buffer.
