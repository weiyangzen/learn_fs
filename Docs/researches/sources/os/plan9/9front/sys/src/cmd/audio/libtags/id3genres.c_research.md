# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/id3genres.c

## Role

This file defines the ID3 genre lookup table used by ID3v1, ID3v2 genre parsing, and M4A numeric genre parsing.

## Main Data

`const char *id3genres[Numgenre]` contains 192 genre names. The table starts with the classic ID3v1 genres such as Blues, Classic Rock, Country, and Dance, and includes later Winamp-style extensions through entries such as Podcast, Indie Rock, G-Funk, Dubstep, Garage Rock, and Psybient.

## Integration

The table is declared in `tagspriv.h` and indexed by:

- `tagid3v1()` for byte 127 of an ID3v1 tag.
- `v2cb()` in `id3v2.c` for numeric `TCON`/genre values.
- `tagm4a()` for non-text `gnre` atoms.

## Risks

Callers must bounds-check indexes against `Numgenre`; the in-tree callers do so before indexing.
