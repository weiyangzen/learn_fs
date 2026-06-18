# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jbig2.mak

Purpose: Ghostscript partial makefile for integrating the `jbig2dec` library.

Build model:
- Supports external linking to `jbig2dec` or compiling selected JBIG2 source files directly into Ghostscript.
- Defines object lists for core arithmetic/generic/refinement/Huffman/MMR/image modules and page/segment/symbol/text/metadata modules.
- Generates `libjbig2.dev` by selecting the shared or compiled module file.
- Provides explicit compile rules for library files plus optional command-line-tool support files such as `getopt`, `sha1`, and `jbig2dec`.

Version notes:
- Comments say the makefile is known to work with jbig2dec v0.7, with one object list known good for v0.2-v0.6.
- Clean targets have comments warning that object/generated file deletion is not selective enough.

Research notes: This file is build glue for an embedded third-party JBIG2 decoder used by Ghostscript image/PDF processing.
