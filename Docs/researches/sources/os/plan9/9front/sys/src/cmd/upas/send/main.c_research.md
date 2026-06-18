# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/main.c

This is the main `upas/send` mail delivery program. It parses dry-run, raw/rmail, debug, interactive, and address-list flags; reads or synthesizes a message; loads rewrite rules; normalizes sender routing; sets a safe reply address; rejects excessive `Received:` loops and overlarge messages; binds destinations; and dispatches to local append, pipe, or refusal paths.

`send()` delegates address resolution to `up_bind()` and adds a `To:` header when needed. Pipe delivery can detach asynchronously for user-submitted mail, batches same-command destinations, sends message text to the child process, captures stderr, and logs or refuses based on process status.

The refusal path builds human-readable bounce text, logs first, then either reports to SMTP/rmail, saves to `dead.letter`, or sends a multipart bounce from postmaster when asynchronous delivery owns the message. This file orchestrates the full send lifecycle and failure semantics.
