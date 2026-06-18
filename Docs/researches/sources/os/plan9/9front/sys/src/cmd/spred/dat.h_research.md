# File Research: sources/os/plan9/9front/sys/src/cmd/spred/dat.h

`spred/dat.h` defines shared data structures, constants, and globals for the `spred` sprite editor.

Key definitions:
- UI constants: border size, minimum window size, selection border size, scrollbar sizes, and rune allocation block size.
- Color-index extension: `DISB` and `NCOLS`.
- Window/file types: `CMD`, `PAL`, `SPR`, `NTYPES`.
- `Wintab`: per-window behavior table with init/die/click/menu/rmb/key/draw/zerox hooks and color slots.
- `Win`: window geometry, image, global/file window links, type, frame state, command-window rune buffer, zoom/scroll data, attached file, and sprite rectangle cache.
- `Ident`: device identity tuple from file metadata.
- `File`: common base struct with type, refcount, file-list links, name, dirty flag, identity, and per-file window list sentinel.
- `Pal`: palette file with colors, 1x1 color images, and selected index.
- `Spr`: sprite file with palette pointer, dimensions, pixel-index data, and palette filename.

Important globals:
- `wlist`, `flist`, `actw`, `actf`, `cmdw`, `scr`, `invcol`, and `quitok`.
