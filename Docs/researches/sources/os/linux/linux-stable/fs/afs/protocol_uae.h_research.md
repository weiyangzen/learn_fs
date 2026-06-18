# File Research: sources/os/linux/linux-stable/fs/afs/protocol_uae.h

## Scope

Defines Universal AFS Error codes used as RxRPC abort values for portable errno-style error reporting.

## API Surface

The file is a single enum mapping UAE-prefixed values from `UAEPERM` through `UAEMEDIUMTYPE`, with numeric values in the `0x2f6df00` range and comments matching Linux errno meanings.

## Dependencies And Risks

Fileserver rotation and RPC error translation compare abort codes from this enum to map remote errors into local `-errno` results. Values must remain wire-compatible; changing them would break protocol interpretation.
