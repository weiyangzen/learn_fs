# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/facpri.c

This file maps syslog facilities and priorities between numeric values and names.

It defines facility table entries for common syslog facilities, optional platform-specific facilities, and local0-local7. `fac_toname()` maps a facility field to text, using direct indexed lookup first and then linear search. `fac_findname()` maps text to facility value.

It also defines priority names and `pri_findname()`/`pri_toname()` for syslog priority values.

Important dependency: `facpri.h` normalizes `LOG_CRON1`/`LOG_CRON2` variants.
