# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/srn.h

## Role

Defines suspend/resume notification event codes and ioctl commands.

## Key Contents

Provides event constants for standby, suspend, resume, battery low, power change, time update, critical suspend, user/system requests, next event, resume/suspend/standby ioctls, and autosx behavior changes.

Defines `srn_event_info_t` with event type `ae_type`.

## Kernel Contents

Under `_KERNEL`, defines clone limit and notification source types for APM and autosx.

## Design Notes

The header warns that these commands and structures may change or disappear, so this is not a stable public contract.
