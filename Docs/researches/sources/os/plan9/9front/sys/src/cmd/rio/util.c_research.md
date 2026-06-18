# File Research: sources/os/plan9/9front/sys/src/cmd/rio/util.c

General `rio` utilities. Converts UTF bytes to runes while tracking consumed bytes/runes/nulls, converts runes to UTF strings, provides checked memory allocation, fatal error handling, rune classification, rune search, and integer min/max.

`error()` aborts or exits all threads depending on `errorshouldabort`.
