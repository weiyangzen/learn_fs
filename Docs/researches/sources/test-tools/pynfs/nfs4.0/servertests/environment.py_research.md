# sources/test-tools/pynfs/nfs4.0/servertests/environment.py

## Purpose
`environment.py` defines the shared NFSv4 server test environment, common assertion helpers, attribute metadata, invalid input generators, and stateid mutation utilities. Test modules receive an `Environment` instance containing configured clients, paths, data samples, security choices, setup/cleanup methods, and helper functions for comparing protocol results.

## Important APIs, Types, And Functions
- `AttrInfo(name, access, sample)` describes an NFS attribute by name, bit number, bitmap mask, access flags, and sample value. Properties classify writable, readable, mandatory, readonly, and writeonly attributes.
- `Environment.attr_info` is a comprehensive table of NFSv4 attrs used by GETATTR/CREATE/SETATTR tests to derive mandatory, unsupported, writable, and sample values.
- `Environment.__init__(opts)` creates `c1` and `c2` `NFS4Client` instances, configures security, long names, sample file/link data, special stateids, and options.
- `_get_security(opts)` chooses auth flavor setup for `none`, `sys`, or `krb5*`.
- `init()` optionally creates the test tree, validates the base path, empties it, and sends a NULL call.
- `_maketree()` creates `/tree` objects for directory, socket, FIFO, symlink, block/char devices, and a regular file with known data.
- `finish()`, `startUp()`, `sleep()`, `serverhelper()`, `clean_sessions()`, and `clean_clients()` provide lifecycle and external server hooks.
- `check(res, stat=NFS4_OK, msg=None, warnlist=[])` is the central status assertion helper, raising `testmod.WarningException` or `FailureException`.
- `checkdict(expected, got, translate={}, failmsg='')` validates returned attribute dictionaries.
- `get_invalid_utf8strings()`, `get_invalid_clientid()`, `makeStaleId()`, `makeBadID()`, `makeBadIDganesha()`, and `compareTimes()` provide shared negative-test inputs.

## Control Flow
The test runner constructs `Environment(opts)`, which creates two clients using selected security credentials. Before test execution, `init()` may build or clean the configured root. `_maketree()` walks the configured path, creates missing path components, resets a `tree` directory, creates special objects, then opens/writes/closes the canonical test file. Each test's `startUp()` sends a NULL RPC to keep the connection warm. After all tests, `finish()` cleans the base path unless cleanup is disabled.

Assertions flow through `check`. It accepts one status or a list, returns silently on expected status, otherwise derives the failing operation name from the last response op or supplied message and raises a testmod exception. `warnlist` converts certain statuses to warnings. Many tests use `t.fail_support` or `t.pass_warn` after a successful `check` to mark unsupported optional server behavior.

`serverhelper` is an integration escape hatch for tests that require out-of-band server-side mutation, especially delegation recall scenarios. It either prompts for manual action or invokes a configured helper command with byte arguments.

## State And Persistence Behavior
The environment stores clients, user/group IDs, option values, sample payloads, and generated stateid constants in memory. It mutates server-side test directories through NFS operations and optionally through an external server helper. It does not persist local metadata except whatever the server stores in the export. Cleanup behavior is option-controlled.

## Dependencies And Integration Points
The module depends on `testmod`, `nfs4lib.NFS4Client`, generated NFS constants/types, `rpc.rpc`, `nfs_ops`, and OS/time helpers. All sibling `st_*.py` modules import `check` and many import mutation helpers. `Environment.attr_info` drives GETATTR/CREATE/ACL tests, while `serverhelper` connects delegation tests to external filesystem mutation tools.

## Risks And Edge Cases
- The header says Python 3.2, while some surrounding pynfs code is Python 2-era; byte/string handling is intentionally mixed and must be preserved.
- `check` treats a string second positional argument as a programmer error by raising a string, which is not valid Python 3 behavior.
- `warnlist` has a mutable default list, though it is not mutated in this function.
- `get_invalid_clientid()` returns `0`, which is only a guessed invalid client ID and may collide with a server's behavior.
- `makeStaleId` and `makeBadID*` intentionally inspect opaque stateid layout and are server-specific; tests using them carry flags such as `staleid` or `ganesha`.
- `_maketree()` may warn rather than fail when special object creation is unsupported, so later tests depend on dependency flags and environment options.

## Test Signals
Every server test module in this group relies on `Environment` and `check`. Meaningful signals include expected NFS status codes, raised warning/failure exceptions, created test tree shape, lease-time sleeps, server helper side effects, and generated invalid UTF-8/stateid/clientid inputs.
