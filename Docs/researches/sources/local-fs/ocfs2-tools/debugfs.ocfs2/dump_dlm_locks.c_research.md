# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump_dlm_locks.c

## Role

`dump_dlm_locks.c` reads and formats live or captured o2dlm lock-resource state from debugfs.

## Input Format

It opens `/sys/kernel/debug/o2dlm/<uuid>/locking_state` through shared debugfs helpers, or a user-specified saved file. It parses records beginning with `NAME:`, `LRES:`, `RMAP:`, `LOCK:`, and optional `LVBX:`.

## Parsed Model

The file builds an in-memory `lockres` with owner, state flags, last-use data, in-flight locks, AST reservations, references, migration/list flags, reference map, optional LVB text, and separate granted/converting/blocked lock queues.

## Output

It decodes DLM lock levels, pending actions, lock-resource states, list membership, reference maps, raw LVB data, and per-lock queue rows with node, current/convert levels, cookie, refs, AST/BAST state, and pending actions.

## Risk Areas

The parser supports only current protocol version 1 for lock resources and locks. Newer kernel debugfs formats are rejected with a diagnostic. Filtering removes matched names from the requested lock list, so duplicate filters are not preserved.
