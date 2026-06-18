# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lhide.c

Moves pixel data between screen and layer save areas during obscuring/exposure.

Key functions:
- `memlhide`: copies visible screen pixels for a layer region into its save area.
- `memlexpose`: restores from save area or calls the layer refresh function.
- `lhideop`, `lexposeop`: callbacks for `_memlayerop`.

Important behavior:
- Hide is skipped if no save area exists.
- Expose on refresh-backed layers invokes `refreshfn` instead of copying from save backing.
