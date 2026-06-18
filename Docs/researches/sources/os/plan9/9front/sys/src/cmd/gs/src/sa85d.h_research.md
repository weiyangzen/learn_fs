# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sa85d.h

Declares the ASCII85Decode filter state and stream template. The state embeds common stream state plus the number of accumulated odd digits and the partial 32-bit word.

It provides the GC descriptor macro, an inline initialization macro used by scanner code to avoid an extra function call, and `s_A85D_template`.

Dependencies are Ghostscript stream common definitions, and `strimpl.h` when templates are referenced.
