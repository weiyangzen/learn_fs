<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/py_net.h -->
# sources/user-network-fs/samba/source3/utils/py_net.h

## Purpose

`py_net.h` defines the C structure backing the `net_s3.Net` Python object.

## Important APIs, Types, and Functions

`py_net_Object` embeds `PyObject_HEAD` and stores `TALLOC_CTX *mem_ctx`, `struct cli_credentials *creds`, `struct loadparm_context *lp_ctx`, `const char *server_address`, and `struct tevent_context *ev`.

## Control Flow

There is no executable logic in the header. `py_net.c` allocates this structure in `net_obj_new()`, reads it in Python method implementations, and frees `mem_ctx` in `py_net_dealloc()`.

## State and Persistence Behavior

The object captures the state required for domain join/leave calls: credentials, configuration, optional target server, and event context. Domain membership persistence is performed by methods using these fields, not by the header itself.

## Dependencies and Integration Points

The struct ties the Python API to Samba talloc, credentials, loadparm, and tevent libraries. It must remain consistent with `py_net_Type.tp_basicsize`.

## Risks and Edge Cases

Ownership of `creds`, `lp_ctx`, and `server_address` is implicit. Any future change to retain borrowed Python data must ensure the C object keeps a valid reference or talloc-owned copy. Adding fields requires care around deallocation and initialization failures.

## Test Signals

Constructor/destructor tests for `net_s3.Net` are the key signal. Leak checks should verify `mem_ctx` and `ev` are released, and method tests should confirm the stored credentials and loadparm context are used for join/leave calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/py_net.h -->
