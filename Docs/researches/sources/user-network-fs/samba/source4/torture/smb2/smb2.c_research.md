# sources/user-network-fs/samba/source4/torture/smb2/smb2.c

## Purpose

`smb2.c` is the registration and wrapper module for Samba's SMB2 torture tests. It provides helper functions for adding tests that need one or two SMB2 tree connections, and `torture_smb2_init()` builds the top-level `smb2` suite by adding simple tests and child suites from many SMB2 torture modules. It does not implement protocol behavior itself; it is the integration point that makes the individual SMB2 test files runnable through the torture framework.

## Important APIs, Types, and Functions

The key local helpers are `wrap_simple_1smb2_test()`, `torture_suite_add_1smb2_test()`, `wrap_simple_2smb2_test()`, and `torture_suite_add_2smb2_test()`. They use `struct torture_context`, `struct torture_suite`, `struct torture_tcase`, `struct torture_test`, and `struct smb2_tree`. They allocate `struct torture_test` records, set `test->run` to a wrapper, store the real function pointer in `test->fn`, and append the test with `DLIST_ADD_END()`.

The central exported function is `NTSTATUS torture_smb2_init(TALLOC_CTX *ctx)`. It creates the `smb2` suite, calls many `torture_smb2_*_init()` child-suite factories, adds simple tests such as `connect`, `setinfo`, `dosmode`, `hold-sharemode`, and `check-sharemode`, sets the suite description, and calls `torture_register_suite()`.

## Control Flow

The one-tree wrapper opens an SMB2 connection with `torture_smb2_connection()`, steals the returned `tree1` under a local `mem_ctx`, invokes the stored test function, and frees `mem_ctx`. The comment explains the ownership trick: some tests close or free their connection, so stealing the tree and freeing the parent avoids double-free patterns. The two-tree wrapper repeats the same setup for `tree1` and `tree2`, handles connection failures with `torture_fail()`, invokes a two-tree function pointer, and frees the shared context on exit.

`torture_suite_add_1smb2_test()` and `torture_suite_add_2smb2_test()` both create a testcase named after the test, allocate and initialize a `struct torture_test`, set `dangerous = false`, and attach it to the testcase list. `torture_smb2_init()` is then a long declarative registration sequence. Registration order matters for how tests appear and run in the torture suite but does not create runtime coupling between child suites beyond shared command-line settings and target connection configuration.

## State and Persistence Behavior

This file maintains no durable application state. It allocates suite/test metadata under the provided talloc context and temporary connection wrappers under per-test memory contexts. Runtime state consists of SMB2 connections created for wrapper tests; freeing the wrapper memory context is expected to release any still-owned connections. The wrappers deliberately tolerate tests that consume or free their own tree connections.

## Dependencies and Integration Points

This is a central integration file. It depends on the torture framework (`torture/smbtorture.h`), SMB2 connection helpers from `torture/smb2/proto.h`, the SMB2 client type definitions, and Samba's linked-list helper. It references a broad set of test factories and test functions implemented in sibling SMB2 torture files, including session, sharemode, setinfo, getinfo, lock, read, create, notify, durable opens, leases, compound operations, oplocks, IOCTLs, rename, crediting, multichannel, timestamps, ACLs, EAs, and more.

## Risks

The wrappers depend on `test->fn` holding function pointers with signatures that match the wrapper selected by registration. A test registered with the wrong helper would compile via the generic storage but fail at runtime due to an invalid call signature. Ownership is also subtle: because individual tests may free connections, changing the talloc-steal/free pattern can reintroduce leaks or double frees. Adding new suites here without including the right prototype can create build failures; adding long-running or manual tests as normal automated tests can affect CI behavior.

## Test Signals

The main signals are structural: the SMB2 suite should register successfully with `NT_STATUS_OK`, one-tree and two-tree tests should establish their required connections before calling test logic, and failures should be reported as torture failures when connection setup fails. Downstream test results come from the registered modules; this file's own correctness is visible when named SMB2 tests appear in the suite and receive the expected number of SMB2 tree connections.
