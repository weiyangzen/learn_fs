# File Research: sources/os/plan9/9front/sys/src/cmd/fax/fax2modem.c

## Purpose
Parses Class 2 fax modem status/result lines into `Modem` state.

## Key Elements
Initializes fax mode and phase, extracts comma-separated numeric parameters after `:`, handles `+FCON`, `+FTSI`, `+FDCS`, `+FCFR`, `+FPTS`, `+FET`, and `+FHNG`, and sets validity bits for captured fields.

## Dependencies
Uses the shared `Modem` structure and error/result constants from `modem.h`.

## Behavior/Risks
Parsing assumes modem responses match expected syntax. `ftsi` stores only the first remote ID seen. `fhng` returns `Rhangup` after recording termination status.
