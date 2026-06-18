# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbwbs.h

Header for BWBlockSort Burrows-Wheeler filters and their block-buffering base state.

It defines `stream_buffered_state_common` with:

- Client-set `BlockSize`.
- Allocated `buffer`.
- Dynamic `filling`, `bsize`, and `bpos`.

It defines `stream_BWBS_state` with inherited buffered state, an `offsets` pointer, current block length `N`, primary index `I`, and current decode index `i`. It aliases this for encode and decode states and declares `s_BWBSE_template` and `s_BWBSD_template`.

This is compression stream state, not filesystem code.
