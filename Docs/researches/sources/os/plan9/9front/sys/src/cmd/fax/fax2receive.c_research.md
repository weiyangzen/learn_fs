# File Research: sources/os/plan9/9front/sys/src/cmd/fax/fax2receive.c

## Purpose
Receives Class 2 fax pages from an already answered modem and writes them into the fax spool.

## Key Elements
Starts page reception with `AT+FDR`, waits for `CONNECT`, creates a page file, sends DC2, copies DLE-escaped page data until DLE/ETX, waits for final modem status, validates `FPTS`/`FET`/`FHNG`, retries failed pages, increments page/document counters, and logs document boundaries.

## Dependencies
Uses modem command/response helpers, `createfaxfile`, `faxrlog`, and `Modem` validity bits.

## Behavior/Risks
The receiver expects `+FCON` has already happened and calls `fcon` to move phase. Multi-document receipt is only partly handled; a comment notes there is no way to run the received hook for a new document, so it remains queued.
