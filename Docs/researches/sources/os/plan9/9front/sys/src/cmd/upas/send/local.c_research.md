# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/local.c

`expand_local()` resolves local mailbox destinations into forwarding, pipe, local append, or unknown-user outcomes. It constructs mailbox paths, rejects `/../` path traversal, reads `forward` files unless already descended from a local forward, detects executable `pipeto` files, and checks mailbox writability before leaving `d_cat`.

The file contains mailbox access logic that approximates permission checks from directory metadata, with comments documenting known Plan 9 mailbox/group limitations. `pipeto` commands are built with `upasname`, original address, and mailbox path arguments.

This is the local-delivery policy bridge between rewrite rules and final mailbox/pipe actions.
