# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdpnext.h

## Role

`gsdpnext.h` is a tiny NeXT Display PostScript compatibility header.

## Contents

It includes:

- `gsalpha.h`
- `gsalphac.h`

No new functions, structs, or macros are defined.

## Integration Notes

This header acts as an API aggregation point for NeXT DPS alpha-related facilities, preserving an include name expected by clients.

## Dependencies

Relies entirely on the included alpha headers.

## Risks

None local beyond include-order dependency. Consumers should include this only when the alpha APIs are desired.
