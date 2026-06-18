# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sa85d.h

Interface and state definition for Ghostscript’s `ASCII85Decode` filter.

It defines `stream_A85D_state` with common stream state plus:

- `odd`: count of accumulated partial ASCII85 digits.
- `word`: accumulated base-85 word.

It also declares:

- GC descriptor macro `private_st_A85D_state`.
- Inline initializer `s_A85D_init_inline`, which sets `min_left`, clears `word`, and resets `odd`.
- External stream template `s_A85D_template`.

This header belongs to Ghostscript stream filtering, not filesystem code.
