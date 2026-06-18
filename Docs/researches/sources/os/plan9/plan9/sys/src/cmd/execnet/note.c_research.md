# File Research: sources/os/plan9/plan9/sys/src/cmd/execnet/note.c

Custom libthread note handling for `execnet`.

Key behavior:
- Maintains per-process note handler slots and delayed note records.
- `threadnotify()` registers/unregisters a handler for the current proc.
- `_threadnote()` captures incoming notes, queues them for the current proc, and defers handling while `splhi` is set.
- Delivers queued notes to registered handlers or exits/aborts/defaults when unhandled.
- `_procsplhi()` and `_procsplx()` control deferred delivery.

Filesystem relevance:
- Supports robust process/thread interruption for pending 9P I/O and child-command handling.
