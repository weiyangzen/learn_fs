# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/wmin.mak

Makefile fragment for compiled Wadalab free Kanji font objects.

Key points:
- Sets `ccfonts_ps=gs_kanji gs_ccfnt`.
- Defines object and stem lists for `wmin` and many `wminrXX` generated C font chunks.
- Covers chunks from `wminr21` through `wminr74`, grouped across `ccfonts1` through `ccfonts7`.
- Comment notes it does not include rules for creating the `wmin*.c` files.

Dependencies and interactions:
- Used by compiled-font build paths through Ghostscript’s `cfonts.mak`-style machinery.
- Supplies object lists, not compile rules.

Research relevance:
- Historical compiled Japanese font packaging support in the Ghostscript build tree.
