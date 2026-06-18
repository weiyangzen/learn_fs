# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcfont.c

Implements composite-font-specific character operators `cshow` and `rootfont`.

Key behavior:
- `cshow` accepts operands in either documented or Adobe-compatible reversed order, sets up a `gs_cshow` text enumerator, and stores the user procedure in `sslot`.
- `cshow_continue` processes text until intervention. On each intervention it pushes character code plus width, constructs an appropriate scaled leaf font, temporarily sets currentfont, and executes the user procedure.
- `cshow_restore_font` restores both root font and current font before continuing.
- `rootfont` returns the current root font dictionary.

Dependencies and coupling:
- Uses `zchar.c` show setup/finish helpers and estack slots.
- Depends on font stack details from `gs_text_enum_t` and on `gs_makefont` for scaled leaf font creation.
- Important for composite fonts because it preserves root/current font distinction during callback execution.
