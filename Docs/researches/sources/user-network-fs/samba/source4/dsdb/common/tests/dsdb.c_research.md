# sources/user-network-fs/samba/source4/dsdb/common/tests/dsdb.c

## Purpose
`tests/dsdb.c` registers a small DSDB torture suite and currently tests that an untrusted LDB search with an explicitly empty attribute list returns entries with zero attributes.

## Important APIs, Types, and Functions
- `torture_ldb_no_attrs()` is the test body.
- `torture_dsdb_init()` creates and registers the `dsdb` torture suite.
- The test uses `ldb_wrap_connect()`, `admin_session()`, `ldb_build_search_req()`, `ldb_req_mark_untrusted()`, `ldb_request()`, and `ldb_wait()`.

## Control Flow
The test obtains the private `sam.ldb` path from loadparm, creates an admin session using the Builtin domain SID, connects to the SAM LDB, builds a subtree search under `cn=users` with `attrs[] = { NULL }`, marks the request untrusted, executes and waits for completion, asserts at least one result, and asserts the first result has `num_elements == 0`.

## State and Persistence
The test is read-only. It depends on an existing `sam.ldb` from a configured test environment and the Users container containing at least one object.

## Dependencies and Integration Points
It integrates with Samba torture registration, LDB wrapper connection, auth session creation, loadparm private paths, and LDB request trust marking. The behavior under test relates to DSDB search filtering and attribute disclosure for untrusted requests.

## Risks and Edge Cases
- The test requires a configured `sam.ldb`; it fails early if run without `-s $SERVERCONFFILE`.
- It assumes the Users container is non-empty.
- It only checks the first result's attributes, not all returned entries.

## Test Signals
This file itself is a test signal for untrusted no-attribute searches. Additional strengthening would assert every result has zero attributes and add a trusted/control comparison.
