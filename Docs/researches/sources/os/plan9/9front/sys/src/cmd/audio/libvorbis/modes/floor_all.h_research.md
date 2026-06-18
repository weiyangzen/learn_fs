# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/floor_all.h

Static floor1 setup presets and floor codebook lists used by Vorbis encoder modes.

Important contents:
- Includes public codec types, backend types, and generated floor codebooks.
- Defines arrays of floor codebook pointers for multiple floor geometries: `128x4`, `256x4`, `128x7`, `256x7`, `128x11`, `128x17`, `256x4low`, `1024x27`, `2048x27`, `512x17`, and LFE `Xx0`.
- Defines `_floor_books[11]`, mapping floor preset index to its book pointer array.
- Defines `_floor[11]`, an array of `vorbis_info_floor1` structures specifying partitions, classes, dimensions, subclasses, subbooks, multiplier, post lists, and fit/error parameters.

Integration points:
- Used by encoder setup code to instantiate floor backends for different sample-rate/quality modes.
- Depends on generated Huffman books from `books/floor/floor_books.h`.

Risk and review signals:
- Static table only; no runtime validation here.
- Post lists and class/subbook references must remain consistent with corresponding codebook arrays.
- LFE floor preset has only edge posts and no books.

Filesystem relevance:
- No filesystem logic. It is static Vorbis encoder setup data.
