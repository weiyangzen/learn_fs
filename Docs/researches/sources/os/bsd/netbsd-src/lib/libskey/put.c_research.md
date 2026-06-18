# File Research: sources/os/bsd/netbsd-src/lib/libskey/put.c

## Purpose
Implements S/Key binary-to-English OTP encoding and English-to-binary decoding using the standard 2048-word dictionary.

## Main Interfaces
Exports `btoe`, `etob`, and `put8`.

## Control Flow And State
The file contains `Wp[2048][4]`, a sorted dictionary of one- to four-character uppercase words. Each word represents an 11-bit value.

`btoe` copies an 8-byte key into a 9-byte working buffer, computes two parity bits by summing 2-bit chunks across the 64-bit key, stores parity in the high bits of the ninth byte, extracts six 11-bit values, and emits six dictionary words separated by spaces.

`etob` copies input to a bounded local buffer, tokenizes exactly six space-separated words, validates word length, normalizes lower-case and common digit substitutions (`1` to `L`, `0` to `O`, `5` to `S`), searches the appropriate dictionary range, inserts each 11-bit value into a bit buffer, checks parity, and copies the first 8 bytes to the caller.

`put8` formats an 8-byte key as four groups of uppercase hex byte pairs.

Internal helpers perform dictionary binary search, bit insertion/extraction across byte boundaries, and word standardization.

## Dependencies
Uses C string/ctype/assert APIs and public constants from `skey.h`.

## Risks And Notes
The encoder assumes the output buffer is large enough for six words and spaces. `etob` truncates/copies input into 36 bytes, matching expected OTP word form but rejecting longer malformed input. The dictionary order is part of the binary-search contract and must not be casually reordered.
