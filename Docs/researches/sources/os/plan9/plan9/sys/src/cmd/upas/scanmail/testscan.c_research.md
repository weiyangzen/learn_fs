# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/testscan.c

## Purpose
Standalone tester for scanmail pattern parsing and canonical matching.

## Behavior
Loads a pattern file, reads messages from a file or stdin, canonicalizes header/body using shared functions, optionally prints canonical text, applies all patterns, prints match context, and exits with the last matched action string.

## Dependencies
`sys.h`, `spam.h`, scanner common functions.

## Risks / Notes
Uses static raw-message state in `canon` to process the first message with headers and subsequent reads without header processing.
