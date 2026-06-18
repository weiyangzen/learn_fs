# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttydev.h

## Purpose
Legacy tty baud-rate constant definitions.

## Main Interfaces
- Defines speed constants from `B0` through `B38400`.
- Defines aliases `EXTA` and `EXTB`.

## Dependencies And Relationships
Used by old tty interfaces and compatibility code; modern terminal code usually gets speed constants through termios.

## Research Notes
The values are compact legacy encodings rather than literal bit-per-second values.
