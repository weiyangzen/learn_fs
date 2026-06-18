# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jbig2.mak

Makefile fragment for integrating the `jbig2dec` library with Ghostscript. It supports either linking to a shared `jbig2dec` library or compiling selected library sources into Ghostscript. Comments note compatibility with jbig2dec v0.7 and older object lists for v0.2 through v0.6.

Defines source/object/generated directories, object groups, headers, optional extra objects, clean targets, compiler command variables, generated `.dev` module rules, and explicit compile rules for JBIG2 arithmetic, Huffman, generic, refinement, image, MMR, page, segment, symbol dictionary, text, metadata, and related support files.

The clean rule contains an explicit warning that object/generated deletion should be more selective.
