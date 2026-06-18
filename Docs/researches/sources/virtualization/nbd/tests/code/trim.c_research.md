# File Research: sources/virtualization/nbd/tests/code/trim.c

## Purpose
Tests that `exptrim()` translates a basic TRIM request into a backend `punch_hole()` call with the expected file descriptor, offset, and length.

## Main Mechanics
Defines a local `punch_hole()` stub that records arguments. Constructs a minimal `SERVER`, `CLIENT`, and one-entry export array, then calls `exptrim()` with a 1 MiB trim from offset zero.

## Dependencies
Uses GLib arrays, pthread mutex initialization, socketpair setup, `nbdsrv.h`, `backend.h`, and `macro.h`.

## Risks and Notes
The test covers the simple single-file case only. It does not validate COW, treefile, readonly, or multifile trim behavior.
