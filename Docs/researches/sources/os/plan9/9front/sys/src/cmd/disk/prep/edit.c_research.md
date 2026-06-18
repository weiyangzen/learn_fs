# File Research: sources/os/plan9/9front/sys/src/cmd/disk/prep/edit.c

## Purpose
Provides the shared interactive partition editing engine used by `prep`, `fdisk`, and `edisk`.

## Key Behavior
- Reads commands from stdin with `getline()`, warning on EOF if changes are unwritten.
- Maintains an ordered in-memory partition list, supports lookup by name, duplicate-name checks, insertion sorted by start offset, and deletion.
- Implements generic commands: set/display dot (`.`), add (`a`), delete (`d`), help (`h`/`?`), print table (`p`), print/update kernel ctl commands (`P`), write (`w`), and quit (`q`).
- Uses `parseexpr()` for start/end expressions with dot, end, total size, and unit scaling supplied by each caller.
- Validates add ranges against current partitions and limits default end prompts to the next partition boundary.
- Delegates storage-specific behavior through callbacks in `Edit`: command extensions, table writes, summaries, kernel partition naming, and name validation.
- Reads the current Plan 9 disk `ctl` partition list, filters to the disk region being edited, and builds `ctlpart` entries for diffing.
- `ctldiff()` deletes changed kernel partitions and emits `part name start end` lines for current in-memory partitions, applying the disk offset.

## Interfaces And Dependencies
- Exposes `getline`, `runcmd`, `findpart`, `addpart`, `delpart`, `editwrite`, `editctlprint`, `ctldiff`, `emalloc`, and `estrdup`.
- Depends on `edit.h` for `Part`/`Edit` and on `<disk.h>` for `Disk`.
- Relies on an external `parseexpr()` implementation declared in `edit.h`.

## Notes
Overlap detection currently formats an error string but does not return it in `addpart()`, so callers primarily prevent overlaps before insertion. `ctldiff()` is the bridge between on-disk table edits and the live `/dev/sd*/ctl` namespace.
