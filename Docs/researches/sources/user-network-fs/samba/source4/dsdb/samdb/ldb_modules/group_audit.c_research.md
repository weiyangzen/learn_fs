# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/group_audit.c

## Purpose
`group_audit.c` logs changes to group membership and user primary groups. It is an LDB module named `group_audit_log` that wraps add and modify requests when logging is enabled, captures pre-operation state when needed, then emits human-readable logs, JSON audit records, and optional messaging notifications after the lower operation reports its final status.

## Important APIs, types, and functions
`struct audit_context` stores module-wide notification state: whether to send events and an `imessaging_context`. `struct audit_callback_context` stores the original request, module, pre-change member list or primary group RID, and a `log_changes` callback.

Core logging helpers include `audit_group_json()`, `audit_group_human_readable()`, `log_primary_group_change()`, `log_membership_change()`, and event-ID mappers `get_add_member_event()` / `get_remove_member_event()`. Difference calculation is handled by `get_parsed_dns()`, `dn_compare()`, and `log_membership_changes()`. Request wrappers are `set_group_membership_add_callback()`, `set_primary_group_add_callback()`, `set_group_modify_callback()`, and `set_primary_group_modify_callback()`. The common completion callback is `group_audit_callback()`.

## Control flow
`group_add()` and `group_modify()` skip replicated updates and do nothing unless human logging, JSON logging, or DSDB group-change notification is enabled. They inspect the request message for `member` or `primaryGroupID`. For membership modify, the module reads the current group with `member` and `groupType` in storage format/reveal-internals mode, stores the old member element, rebuilds the modify request with `group_audit_callback()`, and sends it down. On `LDB_REPLY_DONE`, the callback logs based on the final operation status.

Membership changes are logged by comparing sorted old and new DN arrays. Binary-equal values are ignored; GUID-equal values with changed `RMD_FLAGS` become removed or added events depending on deleted metadata; less/greater comparisons become removals/additions. Primary-group changes are logged by reading `primaryGroupID` and `objectSid`, constructing the primary group SID, resolving that group DN, and emitting a `PrimaryGroup` action. New users with a primary group also cause an added-to-group style event.

## State and persistence behavior
The module does not change directory data. Persistent side effects are audit outputs and optional messages sent with `audit_message_send()` under `DSDB_GROUP_EVENT_NAME` / `MSG_GROUP_LOG`. It uses transaction identifiers from `DSDB_CONTROL_TRANSACTION_IDENTIFIER_OID` when present, but does not manage transactions itself.

## Dependencies and integration points
It depends on Samba audit logging helpers, JSON utilities, Windows event ID constants, DSDB audit helpers for remote address/user SID/session ID/primary DN, parsed-DN utilities from linked attribute support, group type flags, and loadparm configuration `dsdb_group_change_notification`. It relies on lower modules preserving sorted storage-format member values.

## Risks and edge cases
The module deliberately avoids overhead unless logging or notifications are active. Audit quality depends on successful post-operation reads; if the final group cannot be read, it logs a generic failure instead of per-member deltas. There are likely copy/paste fragilities in request fields: some helper paths build modify/search requests using `req->op.add.message` where a modify message would normally be expected, which should be covered by tests. Parsing failures skip per-member audit to avoid breaking the directory operation after persistence.

## Test signals
Exercise add and modify membership changes for every group type to verify Windows event IDs, primary group changes on add and modify, replicated-update bypass, disabled logging bypass, JSON fields including transaction/session/remote/user SID, notification sending when configured, deleted/re-added link metadata via `RMD_FLAGS`, and failure paths when pre/post state reads fail.
