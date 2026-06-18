# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump_dlm_locks.h

## Role

This header defines user-space representations and constants for dumping DLM lock resources.

## Contents

It mirrors DLM lock-resource state flags, queue identifiers (`GRANTED`, `CONVERTING`, `BLOCKED`), and structures for a lock resource and individual locks.

`struct lockres` holds owner/state/counters, optional refmap/LVB strings, and lock queues. `struct lock` holds mode, convert mode, node, AST/BAST flags, pending operation flags, refs, cookie, and list linkage.

## API

It declares `dump_dlm_locks()`, which reads live or saved DLM lock state and prints selected lock resources.
