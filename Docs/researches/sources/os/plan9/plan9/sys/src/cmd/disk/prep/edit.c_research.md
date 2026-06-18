# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/prep/edit.c

This file implements the generic interactive partition-editing command framework used by `fdisk` and `prep`.

Key behavior:
- `getline` reads commands and warns on EOF if changes are unwritten.
- `findpart`, `addpart`, and `delpart` manage sorted `Part` arrays and change flags.
- Base commands:
  - `.`: show/set dot.
  - `a`: add partition using parsed start/end expressions.
  - `d`: delete partition.
  - `h`/`?`: help.
  - `p`: print partition table through caller callback.
  - `P`: print/update sd ctl commands.
  - `w`: write partition table through caller callback.
  - `q`: quit, warning once on unwritten changes.
- `runcmd` tokenizes and dispatches commands, falling back to an editor-specific extension callback.
- `rdctlpart` reads current kernel sd partition lines from the disk ctl fd.
- `ctldiff` compares desired partitions with current ctl partitions, emits `delpart` and `part` commands to reconcile them.
- `emalloc` and `estrdup` are fatal allocation helpers.

Callback model:
- The `Edit` struct supplies disk pointer, partition arrays, and callbacks for add/delete/extra commands/name validation/printing/writing/control printing.

Notable detail:
- Overlap detection builds a warning string but the return is commented out, so overlapping partitions are not rejected by the generic layer.
