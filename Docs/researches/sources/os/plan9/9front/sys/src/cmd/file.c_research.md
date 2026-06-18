# File Research: sources/os/plan9/9front/sys/src/cmd/file.c

## Purpose
Determines file types and optionally emits MIME types.

## Key Elements
Reads up to 6000 bytes, handles UTF BOM conversion, builds character and word histograms, runs a classifier cascade for fixed magics, offset magics, ELF/native executables, scripts, tar, strings, IFF/RIFF, unified diffs, email/mbox, compiler intermediates, source-language heuristics, Plan 9 fonts/images/subfonts, RTF/MS-DOS/icon/face/TGA/Ogg/MP4/MP3, entropy-like compressed/encrypted detection, and English/text fallbacks.

## Dependencies
Uses Plan 9 libc/Bio, libmach executable parsing (`crackhdr`, `objtype`), Rune/UTF support, and Plan 9 file metadata.

## Behavior/Risks
Classifier order is significant and heuristic fallbacks can misclassify short or ambiguous files. Some MIME strings are historical or nonstandard. Several routines mutate the read buffer temporarily while parsing headers or words.
