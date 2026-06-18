<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/adduser.c -->
# sources/user-network-fs/ksmbd-tools/adduser/adduser.c

## Purpose

CLI front end for `ksmbd.adduser`. It parses user-management options, validates the account name, loads config and password database state, dispatches add/update/delete, and notifies mountd.

## Important APIs, Types, and Functions

Important APIs are `adduser_main`, `usage`, getopt descriptors, `command_add_user`, `command_update_user`, `command_delete_user`, `usm_user_name`, `load_config`, `cp_parse_lock`, and SIGHUP notification.

## Control Flow

The parser records the last requested operation, optional password, and custom pwddb/config paths. It requires exactly one USER, validates UTF-8/name rules, loads config, auto-selects add/update by `usm_lookup_user`, calls user_admin.c, then signals mountd if a lock file is available.

## State and Persistence Behavior

Persistent state is the rewritten `ksmbdpwd.db`; config is loaded to enforce delete safety against shares requiring a user.

## Dependencies and Integration Points

Depends on tools, config_parser, management/user, management/share, user_admin.h, and kernel account-name limits.

## Risks and Edge Cases

Operation flags override each other rather than being mutually exclusive errors. A successful database write can still return success if mountd notification fails. Password supplied on the command line is visible to process listings.

## Test Signals

Test add/update/delete/auto behavior, invalid names, colon rejection, empty password handling, custom database paths, user deletion when referenced by shares, and reload notification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/adduser.c -->
