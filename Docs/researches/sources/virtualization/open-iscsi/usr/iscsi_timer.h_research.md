# File Research: sources/virtualization/open-iscsi/usr/iscsi_timer.h

## Purpose
`iscsi_timer.h` declares the `struct timeval` timer helpers from `iscsi_timer.c`.

## Exports
It forward-declares `struct timeval` and exports `iscsi_timer_clear()`, `iscsi_timer_set()`, `iscsi_timer_expired()`, and `iscsi_timer_msecs_until()`.

## Integration Notes
The header deliberately avoids including `<sys/time.h>` by forward declaration, leaving concrete type inclusion to users that allocate or inspect `struct timeval`.
