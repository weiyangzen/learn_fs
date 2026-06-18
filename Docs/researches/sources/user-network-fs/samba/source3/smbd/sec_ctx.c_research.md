# sources/user-network-fs/samba/source3/smbd/sec_ctx.c

## Purpose

`sec_ctx.c` implements the source3 smbd UNIX/security-token context stack. It lets smbd temporarily become root, become an authenticated user, restore previous credentials, and keep the global `current_user` structure synchronized with effective UID/GID, supplementary groups, and NT security tokens. This is central to safe file-service execution because most path, VFS, and share operations rely on the process effective credentials matching the SMB session or temporary root context.

## Important APIs, Types, And Functions

- `unix_token_equal()` compares `security_unix_token` values by UID, GID, group count, and group array bytes.
- `push_sec_ctx()` snapshots the current effective UID/GID, group list, and duplicate NT token into `sec_ctx_stack[++sec_ctx_stack_ndx]`.
- `set_sec_ctx()` and `set_root_sec_ctx()` switch the effective process credentials and update the active stack frame.
- `pop_sec_ctx()` frees the top frame, restores the previous frame's UNIX credentials, and repoints `current_user`.
- `init_sec_ctx()` initializes `sec_ctx_stack[0]` from the process credentials and current groups.
- `sec_ctx_active_token()` walks down the stack to find the most recent non-NULL token during temporary root escalation.
- Static helpers include `become_uid()`, `become_gid()`, `gain_root()`, `get_current_groups()`, and platform-specific `set_unix_security_ctx()`.

The core state comes from `sec_ctx_stack`, `sec_ctx_stack_ndx`, `MAX_SEC_CTX_DEPTH`, `struct sec_ctx`, `struct security_token`, `struct security_unix_token`, and the external `struct current_user current_user`.

## Control Flow

Initialization zeroes the stack, marks all slots invalid, records the initial effective user/group, obtains the supplementary groups through `get_current_groups()`, and initializes `current_user` as guest-like with a NULL NT token. A caller that needs a temporary identity calls `push_sec_ctx()`, then `set_sec_ctx()` or `set_root_sec_ctx()`, and finally `pop_sec_ctx()`. Switching credentials first calls `gain_root()` unless running in non-root mode, then updates supplementary groups with `sys_setgroups()` or Darwin `initgroups`, and finally sets effective GID and UID. After the OS credential switch, the active stack frame is rebuilt and `current_user` is rewritten.

Darwin receives a specialized path because its kernel group list can be a cache; the code follows the required setegid, initgroups, seteuid sequence and caps the group list at `NGROUPS_MAX`.

## State And Persistence Behavior

The file owns in-memory process state only. It mutates real OS effective credentials, group membership, the global context stack, and `current_user`, but does not write persistent storage. The top stack frame owns duplicated group memory and duplicated tokens. A subtle aliasing point is that `current_user.ut.groups` is set to the caller-provided `groups` pointer in `set_sec_ctx_internal()`, while the stack frame stores its own copy. On `pop_sec_ctx()`, `current_user.ut.groups` is repointed to the restored stack frame's group list.

## Dependencies And Integration Points

This module depends on Samba setid wrappers, security token duplication/debugging, profiling macros, global smbd state, `smb_panic()`, `sys_getgroups()`, `sys_setgroups()`, and `reset_chdir_lastconn_cache()`. It integrates with authentication and VFS paths through `current_user`, with root escalation wrappers such as `become_root()`/`unbecome_root()`, and with path access behavior by clearing cached current-directory assumptions after identity changes.

## Risks

Credential switching is high-risk. Stack overflow/underflow panics are intentional safeguards. Failure to restore root in `gain_root()` logs trapdoor warnings but later operations may still be unsafe on unusual systems. Group-list failures panic outside non-root mode. The UID/GID `-1` and 16-bit `65535` warnings flag historically dangerous values but still permit the switch. Any unbalanced push/pop can leave smbd under the wrong credentials. The chdir cache reset is security-relevant because a previously accessible working directory may be inaccessible or misleading under a new user.

## Test Signals

Useful tests include nested `push_sec_ctx()`/`pop_sec_ctx()` balance, `set_sec_ctx()` updating `current_user` and OS effective IDs, root escalation returning to prior tokens, max-depth and underflow panic coverage, Darwin group-list behavior where applicable, and access-control tests that verify VFS operations run under the expected user after session setup and temporary root sections.
