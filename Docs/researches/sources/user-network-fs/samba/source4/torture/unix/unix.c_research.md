# sources/user-network-fs/samba/source4/torture/unix/unix.c

## Purpose
`unix.c` registers the CIFS UNIX extensions torture suite. It groups the UNIX extension tests under the top-level suite name `unix`.

## Important APIs, Types, and Functions
The only function is `torture_unix_init(TALLOC_CTX *ctx)`. It creates a `struct torture_suite`, sets a human-readable description, and registers simple tests `whoami` and `info2` pointing to `torture_unix_whoami` and `unix_torture_unix_info2`.

## Control Flow
At module initialization time, `torture_unix_init()` creates the suite, attaches two simple tests, and calls `torture_register_suite()`. It converts the boolean registration result into `NT_STATUS_OK` or `NT_STATUS_UNSUCCESSFUL`.

## State and Persistence Behavior
The file only mutates the in-process torture suite registry. It creates no remote SMB state itself; the registered tests perform their own connections and cleanup.

## Dependencies and Integration Points
It depends on `torture/smbtorture.h` for registration and `torture/unix/proto.h` for test prototypes. The suite becomes discoverable and runnable through smbtorture after module initialization.

## Risks
Registration failure prevents both UNIX extension tests from being visible. Because this file is only a registry shim, incorrect prototype generation or missing linked test functions will surface as build failures.

## Test Signals
The expected signal is that `smbtorture ... unix.whoami` and `smbtorture ... unix.info2` are listed and runnable.
