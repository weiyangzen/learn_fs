# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/file.c

Purpose: core Vac filesystem implementation layered on Venti files. It implements `VacFs`, `VacFile`, directory metadata handling, traversal, mutation, archive root creation/opening, flushing, syncing, and block-score comparison.

Key structures and model:
- `VacFile` is private here and wraps one Venti file for ordinary data, or two Venti files for directories: `source` for directory entries and `msource` for Vac metadata entries.
- Metadata such as `dir`, `ref`, `removed`, and `dirty` is synchronized by the parent lock. The file comments define an upward locking order: hold child then acquire parent, not the reverse.
- Files are reference-counted and linked in the parent `down` list, so repeated walks share in-memory `VacFile` objects.
- Root opening handles both normal Vac roots and older Fossil-style extra indirection.

Major behavior:
- Reference lifecycle is handled by `filealloc`, `filefree`, `vacfileincref`, and `vacfiledecref`; decrement flushes source/msource and dirty metadata before unlinking from parent.
- Path lookup uses `vacfilewalk`, `dirlookup`, and `fileopensource`, with special handling for `.`, `..`, removed children, snapshots, and Venti entry generation checks.
- Directory enumeration uses `VacDirEnum` through `vdeopen`, `vderead`, `vdeunread`, and `vdeclose`; it flushes dirty in-memory children before direct metablock scanning.
- Metadata block mutation is handled by `filemetaalloc`, `filemetaflush`, and `filemetaremove`; these manage sorted `MetaBlock` entries and can move entries across metablocks when resized.
- File mutation includes `vacfilecreate`, `vacfilesetsize`, `vacfilewrite`, `vacfilesetentries`, `vacfilesetdir`, `vacfilesetqidspace`, and `vacfileremove`.
- Filesystem open/create/sync uses `vacfsopen`, `vacfsopenscore`, `vacfscreate`, and `vacfssync`, with Venti root blocks carrying type `vac`, current root score, block size, and previous score.

Integration points:
- Depends on Venti cache/file APIs such as `vtfileopenroot`, `vtfilecreate`, `vtfileblock`, `vtfileflush`, `vtfilesetentry`, `vtread`, `vtwrite`, and `vtrootpack`.
- Depends on metadata packing helpers in `pack.c` and public API declarations in `vac.h`/`fns.h`.
- Used by `vac.c`, `unvac.c`, and `vacfs.c` for archive creation, extraction, and 9P serving.

Risks and invariants:
- Lock ordering is critical; violating the upward parent-lock rule can deadlock.
- `filemetaflush` contains an unusual unconditional `vdunpack(&f->dir, &me)` immediately after `vdpack`; because `vdunpack` allocates new strings into an existing `VacDir`, this is a maintenance risk and should be reviewed before changing metadata code.
- `vacfilewrite` flushes before the written offset, which is central to Vac’s write-once/cache behavior.
- Venti generation and active-entry checks prevent stale directory references from being treated as valid files.
- `vacfssync` mutates `fs->score` with the newly written root score; callers rely on this when printing `vac:%V`.
