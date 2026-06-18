# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/devnull.c

Purpose: minimal Venti server that accepts writes and syncs but stores nothing.

Behavior:
- Listens on an address, defaulting to `tcp!*!venti`.
- Responds to ping, goodbye, write, and sync.
- Read requests return `no such block`.
- Write requests return the SHA1 score of submitted data without persistence.
- Optional verbose mode logs Venti fcalls.

Integration points:
- Uses Venti server APIs `vtlisten`, `vtgetreq`, and `vtrespond`.
- Useful as a sink/test endpoint for Venti clients.

Risks:
- It can appear to accept writes successfully while guaranteeing future reads fail; only appropriate for tests or benchmarking sinks.
