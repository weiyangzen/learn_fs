# sources/test-tools/pynfs/nfs4.1/server41tests/environment.py

## Purpose
`server41tests/environment.py` defines the shared test environment and helper functions for NFSv4.1 server tests. It creates clients and credentials, prepares a test tree, performs cleanup, wraps common COMPOUND patterns, and centralizes assertions.

## Important APIs, Types, and Functions
- `AttrInfo` models attribute metadata used by tests.
- `Environment(testmod.Environment)` owns primary client `c1`, credentials, test paths, sample file/link data, setup and teardown.
- `Environment.init`, `_maketree`, `finish`, `startUp`, `serverhelper`, `new_verifier`, `testname`, `clean_sessions`, and `clean_clients` implement lifecycle behavior.
- Assertion helpers `fail`, `check`, and `checkdict` raise `testmod` exceptions.
- File/object helpers include `clean_dir`, `do_readdir`, `do_getattrdict`, `create_obj`, `open_create_file`, `open_create_file_op`, `create_file`, `open_file`, `create_confirm`, `create_close`, `write_file`, `read_file`, `get_blocksize`, `close_file`, `maketree`, `lookup_obj`, `rename_obj`, and `link`.

## Control Flow
`Environment.__init__` builds the base `NFS4Client`, initializes the selected auth flavor, establishes default credentials, and sets `opts.home`. `init()` creates a session, optionally builds `/tmp` and `/tree`, verifies and empties the home directory, then destroys leftover sessions and clients. Test helpers produce operation arrays using `nfs_ops.NFS4ops` and call `sess.compound`.

`check()` accepts either one expected status or a list, converts statuses to names, and raises failures or warnings. `open_create_file_op()` is a key composition helper: it chooses the filehandle path, open flag, create mode, claim, owner, access/deny masks, and appends `GETFH`.

## State and Persistence Behavior
The environment keeps per-run unique names based on a timestamp and monotonically increasing verifiers. It creates and cleans server-side files under `opts.home`. Persistent server state is not stored here; the helpers manipulate server state through NFS operations.

## Dependencies and Integration Points
The module depends on `testmod`, `nfs4client`, `nfs4lib`, generated XDR constants/types, `rpc.security`, and `nfs_ops`. Every server41 test module imports at least `check` and often the file/open helpers.

## Risks and Edge Cases
Several defaults are mutable dictionaries in function signatures. Some helpers mix byte strings and text strings depending on call site. `clean_clients` assumes `DESTROY_CLIENTID` support. `makeStaleId` and `makeBadID` are intentionally server-specific. Long sleeps in courtesy tests can dominate runtime.

## Test Signals
Successful setup creates an empty home directory and optional `/tree` with representative object types. Helper-level failures usually indicate protocol regressions in OPEN, CLOSE, CREATE, READ, WRITE, READDIR, GETATTR, layout attribute support, or cleanup operations.
