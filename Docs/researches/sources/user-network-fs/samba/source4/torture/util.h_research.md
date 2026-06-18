# sources/user-network-fs/samba/source4/torture/util.h

## Purpose
`util.h` declares shared SMB1 and general torture utility APIs used across Samba's torture tests. It also defines target-detection macros that let tests adapt expected behavior to Windows, Samba, and other server profiles selected on the smbtorture command line.

## Important APIs, Types, and Functions
Target macros include `TARGET_IS_WINXP`, `TARGET_IS_W2K3`, `TARGET_IS_W2K8`, `TARGET_IS_W2K12`, `TARGET_IS_WIN7`, `TARGET_IS_SAMBA3`, `TARGET_IS_SAMBA4`, `TARGET_IS_W2K16`, and `TARGET_IS_WINDOWS`; they read boolean `torture` settings from the context. Declared helpers cover directory setup, complex file/dir creation, wire string validation, all-info dumping, file attribute and sparse setting, EA checks, opening and closing SMB1 connections, connection-index selection from UNC lists, error checking, multi-process torture execution, adding SMB-specific tests to suites, secondary tree connects, privilege checks, and second-user credential construction.

## Control Flow
The header has no executable flow, but it defines the call surface used by many test files. Suite builders call `torture_suite_add_smb_multi_test()`, `torture_suite_add_2smb_test()`, and `torture_suite_add_1smb_test()` to wrap SMB connection setup around test callbacks. Tests call setup and creation helpers before exercising protocol behavior and use target macros to branch around known server differences.

## State and Persistence Behavior
The declared functions operate on SMB connection state, remote files/directories, EAs, privileges, and credentials. The macros read process-run loadparm settings set by `smbtorture.c`. `torture_user2_credentials()` consumes `torture:user2*` options documented in the comment block.

## Dependencies and Integration Points
The header depends on the generic torture harness and forward declarations for SMB client state, tree state, transport, and credentials. It is the shared interface between raw/basic SMB tests, the runner's target profile settings, and utility implementations elsewhere in `source4/torture`.

## Risks
Because these declarations are broadly consumed, signature changes have large compile-time impact. Target macros only check settings, so misspelled settings or unsupported new targets silently fall back to default behavior. Helpers that mutate server files must be used with safe test shares.

## Test Signals
Indirect signals include successful compilation of all consumers, correct target-specific skips or expected-status branches, reliable SMB connection setup/teardown, and helper-produced failures for setup, EA, privilege, or attribute mismatches.
