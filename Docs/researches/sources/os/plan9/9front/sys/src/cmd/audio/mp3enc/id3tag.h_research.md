# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/id3tag.h

This header declares private ID3 tag state and write functions.

Key structure:
- `struct id3tag_spec`: flags plus pointers/values for title, artist, album, year, comment, track, and genre.

Exports:
- `id3tag_write_v2(lame_global_flags *gfp)`
- `id3tag_write_v1(lame_global_flags *gfp)`

Dependencies:
- Includes `lame.h`.

Integration:
- `lame_internal_flags` embeds or references this tag specification.
- Implemented by `id3tag.c`.
- Tag setter functions are not declared here, likely exposed from another public LAME header.

Risks:
- The structure is labeled private but visible in the header.
- String fields are non-owning `const char *` pointers.
