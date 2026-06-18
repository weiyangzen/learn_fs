# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/unpack.c

Implements `debugreiserfs -u`, reconstructing a filesystem image from the custom pack stream produced by `pack.c`.

Main flow:
- `do_unpack(host, journal_filename, bitmap_filename, verbose)` opens target device/image and optional separated journal target.
- `unpack_partition` validates stream magic and block size, then consumes records until `END_MAGIC`.
- Full-block records are written verbatim.
- Compact leaf records are reconstructed into block headers, item headers, directory entries, stat data, indirect items, and filler direct item bodies.
- A bitmap of unpacked blocks is created when the superblock is encountered and saved at the end.

Supported record types:
- Compact leaves.
- Full blocks.
- Separated journal start/end.
- Unformatted bitmap records, which are skipped.
- End marker.

Reconstruction details:
- Directory entry hashes are recalculated from serialized names when a hash function is available.
- Direct item data is replaced with `'a'` bytes unless it is a safe link.
- Indirect items are expanded from whole arrays or run-compressed pointer sequences.
- Stat data supports old and new formats with compact nlink/size encodings.

Notable risks/quirks:
- Ignores progress text embedded in streams by skipping percent-like tokens.
- Requires separated journal filename if separated journal records are present.
- The output image recreates metadata structure, not original file contents.
