# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stermio.h

## Role

Legacy synchronous terminal/printer channel ioctl definitions and associated structures.

## Key Contents

Defines control-channel commands such as protocol start/halt, printer assignment, polling enable/disable/rate, status reports, and trace channel selection. Defines terminal/printer commands for getting/setting line options, throwing away queued input, getting synchronous line number, and getting all line information.

Defines `struct stio`, mode bits `STFLUSH`, `STWRAP`, and `STAPPL`, status structures `sttsv` and `stcntrs`, and trace message `LOC`.

## Design Notes

This is a legacy terminal compatibility header with fixed ioctl numeric encodings and compact packed-style structures.
