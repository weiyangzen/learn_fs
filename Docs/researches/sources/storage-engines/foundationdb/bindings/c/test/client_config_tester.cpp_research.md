# sources/storage-engines/foundationdb/bindings/c/test/client_config_tester.cpp

## Purpose
Standalone tester for FoundationDB client configuration combinations. It applies requested network options, opens a database, runs a simple transaction, optionally prints client status, and exits according to expected error code.

## Important APIs, types, and functions
`TesterOptions` stores API version, cluster file, external client paths, timeout, trace/tmp settings, expected error, status flag, and arbitrary network options. `extractPrefixedArgument` parses `--network-option-*`; `applyNetworkOptions` resolves generated option names; `testTransaction` performs get/set/commit with `onError` retries; `printDatabaseStatus` emits JSON.

## Control flow
`main` parses arguments, selects API version, applies options before `setupNothrow`, runs the FDB network thread, executes a transaction, stops the network, and compares the observed code to `expectedError`.

## State and persistence behavior
On success it writes `key1=val1`; on status mode it reads client status; trace options create log files. Network options are process-global.

## Dependencies and integration points
Uses SimpleOpt, `test/fdb_api.hpp`, generated option metadata, and platform immediate-exit APIs. Driven by `fdb_c_client_config_tests.py`.

## Risks and test signals
Expected-error handling is the contract. Risks include timeout flakiness, status JSON schema drift, and unknown network option handling. Signals are exact exit code and status JSON fields.
