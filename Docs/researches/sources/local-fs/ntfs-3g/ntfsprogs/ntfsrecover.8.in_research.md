# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsrecover.8.in

## Role

`ntfsrecover.8.in` is the manual page template for `ntfsrecover`, documenting recovery of Windows-committed NTFS metadata transactions from `$LogFile`.

## Conceptual Model

The page explains NTFS metadata updates as transactions: multiple metadata records must be updated together, and Windows logs requested metadata actions before applying them. If interruption occurs after commit, the log can be replayed to restore metadata consistency.

`ntfsrecover` applies committed Windows log actions that were not completed. It does not recover user data updates, and it cannot repair Linux-side crashes because ntfs-3g does not log its own metadata updates.

## Documented Interface

Normal usage is no option or `-s/--sync`.

Developer/inspection options include:

- `-b/--backward`: inspect log actions backward without applying updates.
- `-f/--forward NUM`: inspect forward without applying updates.
- `-r/--range BLOCK-RANGE`: inspect a log block range.
- `-c/--clusters CLUSTER-RANGE`: filter output by affected clusters.
- `-t/--transactions COUNT`: display transaction parameters.
- `-p/--play COUNT`: undo transaction sets and redo one.
- `-u/--undo COUNT`: undo transaction sets.
- `-k/--kill-fast-restart`: apply log changes and discard Windows fast-restart cached changes.
- `-n/--no-action`, `-v`, `-V`, `-h`.

## Safety Notes

The page explicitly marks `--kill-fast-restart` as dangerous and data-loss-prone. It also notes that undo/play operations may not always be possible because some actions are not undoable.

## Relationship To Build

`Makefile.am` builds `ntfsrecover` from `playlog.c`, `ntfsrecover.c`, `utils.c`, `utils.h`, and `ntfsrecover.h`; those implementation files are outside this work item.
