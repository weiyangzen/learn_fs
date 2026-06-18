# File Research: sources/os/plan9/9front/sys/src/cmd/dict/pcollinsg.c

Adapter for German Paperback Collins binary-ish markup.

Key elements:
- Input uses byte `0x05...0x06` font escapes and `0xba...0xba` numeric special escapes.
- `intab` maps source bytes to runes or sentinels.
- `numtab` maps numeric special codes to runes.
- `overtab` maps overstrike accent characters to internal accent ligatures.
- `pcollgprintentry` decodes font escapes, headword font selection, numeric specials, and overstrike accents.
- `pcollgnextoff` scans for the font escape sequence marking a headword; falls back to a carriage-return boundary.
- `reach` reads escape payloads into `tag`.

Dependencies:
- Uses ligature lookup and output helpers.

Research notes:
- Used by German-English and English-German Collins entries.
- Unknown numeric specials are emitted as `\N'...'`-style text.
