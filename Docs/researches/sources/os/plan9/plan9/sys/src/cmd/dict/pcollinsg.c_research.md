# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/pcollinsg.c

Implements callbacks for the Paperback Collins German format. This format uses byte escapes `0x05...0x06` for font/style tags and `0xba...0xba` numeric symbol escapes.

`intab` maps all 256 input bytes to output runes or internal sentinel codes. `numtab` converts numeric symbol escapes to runes, mostly phonetic and typographic symbols. `overtab` maps overstrike/accent characters to shared ligature accent codes.

`pcollgprintentry` streams the entry byte by byte. Font escape tags are gathered by `reach`; the first tag byte controls headword filtering, with font `h` treated as headword text. Numeric symbol escapes are looked up in `numtab`; unknown numeric escapes are printed as `\N'...'`. A caret byte begins an overstrike/accent sequence, which attempts ligature composition with the previous rune or emits a fallback caret/accent representation.

`pcollgnextoff` searches for the `0x05 'h' 0x06` headword marker. It also remembers the most recent carriage-return offset and returns it at EOF as a fallback definition boundary. `pcollgprintkey` has no implemented key.

Integration points: registered in `utils.c` for Collins German-English and English-German dictionaries. Depends on shared output and ligature helpers.

Risks and notes: the parser is byte-format-specific and treats font tags mostly as output suppression/selection, not style. `reach` truncates tags at 31 bytes. Unknown symbol escapes degrade to visible escape text.
