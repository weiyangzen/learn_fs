# File Research: sources/local-fs/mtd-utils/nandtest.c

## Purpose
Destructive NAND erase/write/read verification test with optional content restoration.

## Key Elements
Parses pass count, read count, random seed, offset, length, mark-bad, and keep-content options. For each eraseblock, skips known bad blocks, generates random data, optionally saves old contents, erases, writes, repeatedly reads and compares, reports ECC corrections/failures, and optionally restores saved contents.

## Dependencies
Uses Linux MTD ioctls `MEMGETINFO`, `MEMGETBADBLOCK`, `MEMERASE`, `MEMSETBADBLOCK`, and `ECCGETSTATS`.

## Behavior/Risks
Destructive by default. Offset and length must be eraseblock-aligned. `--keep` reduces but does not eliminate risk because failed erase/write/restore operations can still destroy data.
