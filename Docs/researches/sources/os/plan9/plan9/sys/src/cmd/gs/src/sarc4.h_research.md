# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sarc4.h

Header for the Arcfour stream cipher filter.

It defines `stream_arcfour_state` with common stream state, two permutation indices `x` and `y`, and the 256-byte S-box. It declares:

- `s_arcfour_set_key`.
- GC descriptor macro `private_st_arcfour_state`.
- External `s_arcfour_template`.
- `s_arcfour_process_buffer` for in-place buffer transformation.

This is a Ghostscript/PDF stream cipher interface, not filesystem logic.
