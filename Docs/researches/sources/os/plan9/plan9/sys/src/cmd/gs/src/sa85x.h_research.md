# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sa85x.h

Interface header for ASCII85 stream filters, adding `ASCII85Encode` state on top of `sa85d.h`.

It defines `stream_A85E_state` with common stream state plus:

- `count`: number of emitted digits since the last line break.
- `last_char`: last written character.

It declares the GC descriptor macro `private_st_A85E_state`, inline initializer `s_A85E_init_inline`, and external `s_A85E_template`.

The actual encode implementation is elsewhere. This is stream filter interface code, not filesystem logic.
