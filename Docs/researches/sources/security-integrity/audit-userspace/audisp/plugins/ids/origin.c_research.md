# sources/security-integrity/audit-userspace/audisp/plugins/ids/origin.c

Purpose: tracks remote IPv4 origins, their accumulated karma score, and whether they are currently blocked.

Important APIs and data: exports initialization, traversal, creation/destruction, add/find/delete/current access, score adjustments, login anomaly helpers, IPv4 conversion helpers, and `unblock_origin`.

Control flow: origins are stored in an AVL tree keyed by integer IPv4 address. Bad service/root login helpers log audit anomaly events and add configured weights. `bad_login_origin` increments by failed-login weight. `unblock_origin` finds by dotted string and clears the blocked flag.

State and persistence: global static AVL tree plus global `cur` pointer are process-local only. Blocking state is mirrored in firewall side effects via `reactions.c` but the origin table itself is not persistent.

Dependencies and integration: depends on `avl`, global debug logging from `ids.h`, audit response logging, config weights, and reaction unblocking. Event models use `current_origin` after lookups/scoring.

Risks: address handling is IPv4-only and byte-order-sensitive; unknown addresses may collapse into `255.255.255.255` or zero-like values depending caller behavior. `sockint_to_ipv4` returns a static buffer. AVL comparator subtracts unsigned addresses through signed int return, which can overflow ordering for far-apart values.

Test signals: add/find/delete duplicates, score increments, audit anomaly logging inputs, dotted conversion round trips, and timed unblock behavior.
