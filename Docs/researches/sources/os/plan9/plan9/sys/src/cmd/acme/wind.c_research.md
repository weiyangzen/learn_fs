# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/wind.c

Implements Acme `Window` lifecycle, layout, tag maintenance, dirty-state presentation, and event buffering.

Key functions:
- `wininit` initializes tag/body `Text` structures, clone state, fonts, scroll/button drawing, file menu, and dirty/scratch flags.
- `winresize` lays out the tag, border, body, and modified button, while preserving maximum body line tracking.
- `winlock`, `winunlock`, and `winclose` coordinate reference counting and locking across all windows sharing the same body file.
- `winsettag1` reconstructs the tag command prefix (`Del`, `Snarf`, `Undo`, `Redo`, `Put`, `Get`, `Look`) and preserves user selection around the `|`.
- `wincommit` commits cached text and treats a tag filename edit as a body file rename.
- `winevent` appends owner-tagged event text and wakes a pending event reader.

Interactions:
- Depends on Acme `Text`, `File`, `Column`, `Row`, `rfget`, `fileaddtext`, `textresize`, `textinsert`, `textdelete`, and `fileundo`.
- Works with `xfid.c` via `eventx`, `events`, `ctlfid`, `nopen`, and window control/event files.

Notable details:
- `winunlock` walks shared text windows backward because closing one window can mutate the shared `File` text list.
- Scratch windows include `/guide` and `+Errors`; they are exempt from dirty-close warnings.
- Include directories are stored as front-inserted rune strings after validation with `dirstat`.
