# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/bind.c

## Purpose
Destination binder for `upas/send`, resolving addresses into local delivery, pipes, aliases, translators, authorization, or errors.

## Main Interfaces
- `up_bind`: iterative binding loop over destination lists.
- `forward_loop`: detects excessive local-system hops in bang paths.

## Behavior
Initial pass escapes destinations, checks forwarding loops and shell characters, then repeatedly applies rewrite rules and expands results for up to 32 iterations. It handles authorization, local forward files, local `pipeto`, alias expansion, translator output, and grouping of bound destinations.

## Dependencies
`rewrite`, `authorize`, `expand_local`, `translate`, destination list utilities.

## Risks / Notes
Unresolved destinations after 32 passes are marked forwarding loops.
