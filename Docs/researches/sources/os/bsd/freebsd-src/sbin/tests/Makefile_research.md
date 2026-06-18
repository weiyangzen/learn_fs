# File Research: sources/os/bsd/freebsd-src/sbin/tests/Makefile

## Purpose
Top-level test makefile for `sbin` tests.

## Main Elements
- Sets `.PATH` to `${SRCTOP}/tests`.
- Enables `KYUAFILE=yes`.
- Includes `bsd.test.mk`.

## Dependencies And Integration
Creates the Kyua test directory integration point for `sbin`.

## Risk Notes
Build orchestration only.
