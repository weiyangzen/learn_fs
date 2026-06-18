# File Research: sources/os/plan9/9front/sys/src/cmd/truetypefs.c

This program is a 9P file server exposing TrueType fonts as Plan 9 font/subfont files under `/n/ttf`. Font names are expected as `<fontname>.<size>`, resolved under `/lib/font/ttf` by default or `-F fontpath`.

`tryfont()` opens and caches `TTFont` instances. `mksubfonts()` builds a Plan 9 `font` file listing Unicode ranges split into 256-codepoint subfonts. `compilesub()` lazily renders glyphs into Plan 9 subfont bitmap format using libttf glyph metrics and bitmap data.

The 9P handlers support attach, clone, walk, stat, and read. A font directory contains `font` plus generated `s.xxxx-yyyy` subfont files. Data is cached per subfont after first read.
