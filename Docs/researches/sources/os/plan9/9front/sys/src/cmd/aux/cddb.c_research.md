# File Research: sources/os/plan9/9front/sys/src/cmd/aux/cddb.c

Role: CDDB/GNUDB client that queries album metadata from a disc ID and track offsets.

Inputs and options:
- Usage expects `query diskid n offset... leadout`.
- `-s` chooses the server, default `gnudb.org`; `-D` enables protocol tracing; `-t`/`-T` add track and total durations; `-e dir` emits FLAC encoding commands.

Protocol flow:
- Dials TCP port 8880, sends `cddb hello`, selects protocol level 6 for UTF-8, sends `cddb query`, accepts exact or first close match, then issues `cddb read`.
- Parses `DTITLE`, `DYEAR`, and `TTITLEn` records.
- Splits `artist / title` strings into separate artist and title fields.

Output:
- Default output is tab-separated album and track metadata.
- Encoding mode prints commands that read `/mnt/cd/aNNN` through `audio/flacenc` with Vorbis-style tags.

Data model:
- `Toc` stores album metadata and up to 64 `Track` entries.
