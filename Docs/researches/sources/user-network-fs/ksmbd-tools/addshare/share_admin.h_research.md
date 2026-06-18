<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/share_admin.h -->
# sources/user-network-fs/ksmbd-tools/addshare/share_admin.h

## Purpose

Small public header for addshare command implementations.

## Important APIs, Types, and Functions

Defines `command_fn` as `int(char *smbconf, char *name, char **options)` and declares `command_add_share`, `command_update_share`, and `command_delete_share`.

## Control Flow

`addshare.c` selects one command and transfers ownership of path/name/options to it. The implementation frees those inputs on exit.

## State and Persistence Behavior

No direct persistence. The declared functions persist by rewriting `ksmbd.conf`.

## Dependencies and Integration Points

Included by addshare.c and share_admin.c.

## Risks and Edge Cases

The ownership convention is implicit; future callers must not reuse arguments after command invocation.

## Test Signals

Compile coverage plus CLI add/update/delete tests validate the contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/share_admin.h -->
