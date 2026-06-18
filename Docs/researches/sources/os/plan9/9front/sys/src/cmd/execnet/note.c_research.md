# File Research: sources/os/plan9/9front/sys/src/cmd/execnet/note.c

This file overrides/augments libthread note handling for execnet. It is explicitly marked `BUG BUG BUG` and includes private `threadimpl.h`.

Key responsibilities:
- Implements `threadnotify` registration keyed by process pid.
- Stores delayed notes in a fixed `notes[128]` table.
- Delivers pending notes when a proc leaves splhi state.
- Implements `_threadnote`, `_procsplhi`, and `_procsplx`.

Important implementation notes:
- Notes are associated with `Proc*` and delivered to handlers registered for that proc’s pid.
- Unhandled notes either fall back to default handling, abort on `sys:` notes, or exit all threads.
- `"threadint"` notes are continued immediately.
- This file reaches into libthread internals and should be treated as compatibility/special-case code rather than ordinary application logic.
