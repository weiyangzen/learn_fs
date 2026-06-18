# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/id3tag.c

This file implements ID3v1 and simple ID3v2 tag writing for the LAME-derived encoder.

Key responsibilities:
- Maintains standard ID3 genre names and an alphabetical genre listing map.
- Stores user-provided title, artist, album, year, comment, track, and genre in `gfc->tag_spec`.
- Controls whether ID3v1, ID3v2, padding, or spacing is used.
- Writes ID3v2.3 text/comment frames into the bitstream.
- Writes ID3v1/1.1 fixed-size trailing tags into the bitstream.

Important functions:
- `id3tag_genre_list(...)`: iterates genres in alphabetical order through a callback.
- `id3tag_init(...)`: clears tag state and sets unknown genre.
- `id3tag_add_v2()`, `id3tag_v1_only()`, `id3tag_v2_only()`, `id3tag_space_v1()`, `id3tag_pad_v2()`: set policy flags.
- `id3tag_set_title()`, `id3tag_set_artist()`, `id3tag_set_album()`, `id3tag_set_year()`, `id3tag_set_comment()`, `id3tag_set_track()`, `id3tag_set_genre()`: populate metadata.
- `id3tag_write_v2()`: builds and writes an ID3v2.3 tag.
- `id3tag_write_v1()`: builds and writes a 128-byte ID3v1 tag.

Dependencies and integration:
- Includes `lame.h`, `id3tag.h`, `util.h`, and `bitstream.h`.
- Uses `add_dummy_byte()` to insert tag bytes into the encoder's bitstream.
- `lame.c` writes ID3v2 before the Xing VBR header and ID3v1 during flush.

ID3v2 behavior:
- Writes `ID3` header version 2.3.0.
- Uses ISO-8859-1 text encoding byte `0`.
- Supports frames `TIT2`, `TPE1`, `TALB`, `TYER`, `COMM`, `TRCK`, and `TCON`.
- Adds optional 128-byte padding.
- Does not perform unsynchronization.

ID3v1 behavior:
- Writes `TAG`, 30-byte title/artist/album, 4-byte year, comment, optional track byte, and genre byte.
- Uses zero padding or space padding depending on flag.
- Uses ID3v1.1 track convention when a track is set.

Risks and edge cases:
- Stores string pointers, not copies, so caller-provided strings must remain valid until tags are written.
- `local_strcasecmp()` calls `tolower()` on `char` values without an explicit unsigned cast.
- ID3v2 tag size is encoded as synchsafe 28-bit, but the code does not guard against extremely large total tag sizes.
- Genre name list includes historical Winamp spellings, including offensive legacy genre names.
