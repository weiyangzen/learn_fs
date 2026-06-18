# File Research: sources/os/plan9/plan9/sys/src/cmd/freq.c

This is a character/rune frequency counter. It reads stdin or named files, counts occurrences in a `Runemax+1` array, and prints nonzero counts in selected formats.

Flags choose decimal, hex, octal, printable character, and rune-aware input. Without numeric/character format flags, it defaults to decimal, hex, octal, and character output.

It uses Plan 9 `Biobuf` APIs and reports read errors after `Bterm`.
