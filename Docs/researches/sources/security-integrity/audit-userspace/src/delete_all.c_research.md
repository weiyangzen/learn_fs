# sources/security-integrity/audit-userspace/src/delete_all.c

Purpose: implements `delete_all_rules`, the auditctl helper that enumerates kernel audit rules and deletes the rules selected by the process-wide `key_match` predicate. It is a small bridge between libaudit netlink rule listing and the local linked-list representation used by auditctl.

Important APIs/functions: exports `delete_all_rules(int fd)`. It calls `audit_request_rules_list_data`, waits with `select`, reads replies with `audit_get_reply`, filters `AUDIT_LIST_RULES` records through external `key_match`, stores copies in `llist` via `list_append`, and deletes them with `audit_send(fd, AUDIT_DEL_RULE, ...)`. It uses `audit_msg` for error reporting and `list_clear` for cleanup.

Control flow: the function requests a rule dump and rejects non-positive sequence ids. It initializes an `llist`, then loops up to 40 tenths of a second, resetting the timeout counter whenever a reply arrives. Replies with a different netlink sequence are ignored. `NLMSG_DONE` ends collection, `NLMSG_ERROR` with a kernel error aborts, non-rule replies are skipped, and matching rules are copied into the list. After collection it iterates the saved list and sends each rule back as an `AUDIT_DEL_RULE` request.

State and persistence: no persistent process state is owned here. It temporarily persists matching rule blobs in an in-memory list so deletion happens after the listing pass, avoiding mutation while the kernel dump is being consumed. Kernel audit rule state is changed only by the final `AUDIT_DEL_RULE` sends.

Dependencies and integration: depends on `libaudit.h`, audit private helpers, `auditctl-llist.h`, POSIX `select`, and netlink reply structures. It is part of audit-userspace command handling and relies on the caller to supply an audit netlink fd and define the active deletion filter through `key_match`.

Risks: `fd_set read_mask` is initialized once before the loop; because `select` can mutate fd sets, reuse without reinitializing could miss readiness on some platforms. The select result is ignored and `audit_get_reply` is attempted nonblocking every iteration, which is deliberate but can make timeout behavior dependent on libaudit nonblocking semantics. Partial deletion failures leave earlier rules deleted and later rules intact. Correctness depends on `list_append` making a deep copy of `rep.ruledata` because the reply buffer is reused.

Test signals: exercise with a fake or test audit netlink endpoint that emits mixed sequence numbers, `NLMSG_DONE`, `NLMSG_ERROR`, and matching/nonmatching `AUDIT_LIST_RULES`. Integration tests should verify that only `key_match` rules are deleted, timeout with no replies returns success with no deletion, and send failures abort with list cleanup.
