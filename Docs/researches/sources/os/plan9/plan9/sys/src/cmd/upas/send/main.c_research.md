# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/main.c

## Purpose
Main mail delivery program. It reads a message, normalizes sender/header context, resolves destinations, performs local/pipe delivery, and handles bounce/refusal behavior.

## Main Interfaces
- `main`: argument parsing, message read/default creation, rewrite setup, gateway normalization, loop/size checks.
- `send`: binds destinations and dispatches by status.
- `pipe_mail`: executes command deliveries.
- `complain_mail`, `refuse`, `replymsg`: refusal/bounce handling.
- `save_mail`: saves interrupted or failed interactive mail to dead.letter.

## Behavior
Supports dry-run/list modes, rmail mode, debug, no-input mode, and interrupt saving. It protects sender strings from shell characters, rejects excessive Received loops and oversized messages, groups destinations by action, optionally daemonizes before pipe delivery, logs results, and generates multipart bounce mail for non-bulk failures.

## Dependencies
`message.c`, rewrite/bind/local/dest/log modules, process/stream helpers, mailbox path helpers.

## Risks / Notes
- Asynchronous pipe delivery exits parent early to reduce user wait.
- Bulk mail is not bounced.
- Out-of-resource refusals request retry instead of permanent failure in rmail mode.
