# File Research: sources/os/plan9/9front/sys/src/cmd/fax/modem.h

## Purpose
Declares the fax modem state structure, result/error codes, validity flags, and cross-module functions.

## Key Elements
`Modem` stores data/control fds, modem ID/type, response/error buffers, fax phase, remote ID, FDCS/FPTS/FET/FHNG status, page spool identity, input buffer, Bio page input, and current page geometry. Enumerations define response classes, public error codes, and valid-field bits.

## Dependencies
Requires Bio and the fax C modules that implement modem parsing, sending, receiving, file handling, and logging.

## Behavior/Risks
The header advertises `setflow`, `setspeed`, and `faxxlog`, but this file group only contains `xonoff`, `faxrlog`, and other helpers. Error strings are indexed by enum value in `subr.c`, so enum/table consistency matters.
