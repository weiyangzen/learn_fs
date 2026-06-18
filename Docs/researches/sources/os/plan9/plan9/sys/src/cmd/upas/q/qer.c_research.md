# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/q/qer.c

## Purpose
Queue entry writer for upas queued delivery.

## Behavior
Creates a per-user or specified queue directory, writes stdin to a generated `D.*` data file, optionally copies associated `-f` files as `F*`, then creates a locked `C.*` control file containing delivery arguments and associated file names. The data file is created before the control file so `runq` does not see incomplete entries as runnable.

## Dependencies
Plan 9 `String`, queue directory conventions (`C.*`, `D.*`, `F*`), `syscreatelocked`.

## Risks / Notes
Logs if data does not start with `From`; read errors from stdin are intentionally ignored/commented out.
