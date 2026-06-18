# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/spam.h

## Purpose
Shared constants, action IDs, pattern data structures, globals, and prototypes for scanmail.

## Contents
Defines action order (`Dump`, `HoldHeader`, `Hold`, `SaveLine`, `Lineoff`), hash and buffer sizes, pattern types (`regexp`, `string`), `Spat`, `Pattern`, and `Patterns` structures, plus externs for scanner globals and common functions.

## Dependencies
Plan 9 regexp `Reprog`/`Resub` and `Biobuf`.

## Risks / Notes
Action order is semantically important: `Dump` has highest priority and `Lineoff` must be last.
