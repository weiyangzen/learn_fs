<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/user_admin.h -->
# sources/user-network-fs/ksmbd-tools/adduser/user_admin.h

## Purpose

Public command header for adduser operations.

## Important APIs, Types, and Functions

Defines `MAX_NT_PWD_LEN` as 129 and declares `command_fn` plus add, update, and delete command functions.

## Control Flow

The CLI selects a command and transfers ownership of pwddb/name/password strings to the implementation.

## State and Persistence Behavior

No direct persistence; declared commands rewrite `ksmbdpwd.db`.

## Dependencies and Integration Points

Included by adduser.c and user_admin.c.

## Risks and Edge Cases

Ownership semantics are implicit and should be documented if reused.

## Test Signals

Validated by compile coverage and adduser CLI behavior tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/user_admin.h -->
