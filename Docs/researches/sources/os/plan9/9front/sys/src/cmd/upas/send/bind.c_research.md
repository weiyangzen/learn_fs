# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/bind.c

`up_bind()` resolves a list of destination addresses into concrete delivery actions. It first escapes addresses, checks forwarding loops in both destination and sender paths, rejects shell metacharacters, then iteratively applies rewrite rules, authorization, alias expansion, local mailbox expansion, and translation commands.

The resolution loop alternates between two work lists for up to 32 passes; unresolved entries after that become `d_loop`. Successful terminal entries are grouped with `d_same_insert()` so similar local or pipe deliveries can be batched.

`forward_loop()` detects repeated appearances of the local system in bang paths, guarding against external forwarding cycles. This file is the central address-binding state machine for `upas/send`.
