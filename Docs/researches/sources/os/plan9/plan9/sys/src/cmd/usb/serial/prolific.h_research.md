# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/prolific.h

Prolific PL2303 protocol and device constants.

Defines:
- Device flavor/revision constants.
- PL2303 class/vendor request IDs and line coding sizes.
- Interrupt status bit definitions.
- Device control register indices/values and pipe reset commands.
- VID/DID constants for Prolific and many rebadged USB serial cables.
- Exports `plops` and `plmatch`.

This header supplies the lookup table constants and request encodings used by `prolific.c`.
