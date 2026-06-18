# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/ml/dat.h

## Purpose
Shared declarations for the mailing-list programs.

## Contents
Defines `Addr` linked-list nodes, globals for parsed headers and list addresses (`from`, `sender`, `firstfield`, `na`, `al`), includes SMTP parser headers, and declares helper functions from `common.c`.

## Dependencies
`../smtp/smtp.h`, `../smtp/y.tab.h`, `String`, parser `Field`/`Node`.

## Risks / Notes
Globals are shared across small single-purpose programs rather than encapsulated.
