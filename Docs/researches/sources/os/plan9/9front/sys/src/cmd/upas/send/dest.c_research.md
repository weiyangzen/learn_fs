# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/dest.c

This file implements destination objects and their circular list mechanics. `dest` entries can be queued by `next` and grouped by `same`; grouped entries share a delivery command/mailbox and cap batch size with `MAXSAME` and `MAXSAMECHAR`.

`d_new`, `d_free`, `d_rm`, `d_insert`, `d_rm_same`, and `d_same_insert` form the destination container API. `d_same_insert()` also suppresses duplicate delivery arguments and groups only local mailbox or pipe actions.

`d_to()` synthesizes a `To:` header from destination groups, with special handling for `local!`. `s_to_dest()` parses whitespace-separated destination strings, preserving quoted fields, rejects shell characters, creates child destinations, and inherits authorization from the parent.
