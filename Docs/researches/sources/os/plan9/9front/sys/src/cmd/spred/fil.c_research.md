# File Research: sources/os/plan9/9front/sys/src/cmd/spred/fil.c

`spred/fil.c` implements shared file-list, identity, title, dirty-state, and write helpers for palettes and sprites.

Key responsibilities:
- `tline`: reads logical file-format lines, strips comments outside quoted regions, tokenizes fields, and skips blank/comment-only lines.
- `getident`: captures file identity from `dirfstat`; `putident` is a no-op placeholder.
- `identcmp`: compares file identities by type, dev, and qid path.
- `filcmp`: orders files by type then name.
- `filinit`: initializes a `File`, assigns its name, creates empty window-list sentinel links, and inserts into sorted global `flist`.
- `putfil`: dispatches type-specific cleanup, removes from file list, and frees common storage.
- `filtitlelen`/`filtitle`: produce menu titles showing dirty flag, window count marker, active-file marker, and filename.
- `winwrite`: dispatches active window write to palette or sprite writer.
- `filredraw`: redraws all windows attached to a file.
- `change`: marks a file dirty and clears `quitok`.

Important interactions:
- Used by `pal.c`, `spr.c`, `spred.c`, and window-management code.
