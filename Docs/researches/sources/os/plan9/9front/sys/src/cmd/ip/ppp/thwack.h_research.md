# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/thwack.h

This header defines Thwack codec limits, state structures, and exported functions.

Important constants include `ThwMaxBlock` 1600, `HashLog` 12, `MinMatch` 3, encoder/decode window sizes of 64 blocks, and history encoding bounds such as `CompBlocks`, `MaxSeqMask`, and `MaxSeqStart`.

`ThwBlock` describes an encoder history block with sequence number, acknowledgment status, rolling hash table, byte range, and offset metadata. `Thwack` contains the encoder slot pointer, per-slot block descriptors, hash tables, and retained `Block` pointers.

`UnthwBlock` and `Unthwack` are the decoder-side history store. The decoder uses fixed byte arrays per slot rather than retaining input `Block`s.

Exports are `thwackinit`, `thwackcleanup`, `thwack`, `thwackack`, `unthwackinit`, `unthwack`, `unthwackstate`, and `unthwackadd`.
