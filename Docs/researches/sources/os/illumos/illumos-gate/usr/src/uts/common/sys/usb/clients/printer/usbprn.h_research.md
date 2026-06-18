# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/printer/usbprn.h

Internal USB printer driver state header. It defines transfer timeouts, per-pipe state flags, max transfer size, per-pipe state `usbprn_ps_t`, PM state `usbprn_power_t`, and per-instance `usbprn_state_t`.

`usbprn_state_t` holds USBA registration, descriptors, device ID buffer, default/bulk pipes, serialization objects, pending bulk message/buf state, port status, power state, ECPP/printer timeout settings, logging, and ugen support.

Macros cover device-access checks, pipe busy checks, debug masks, device ID maximum, and minor-number extraction for ugen-style minors.

Notable detail: `USBPRN_PIPES_BUSY()` references `usbprn_default.ps_flags`, but the state structure has `usbprn_def_ph` rather than a `usbprn_default` pipe-state member. This looks like stale macro code unless supplied by another compatibility definition.
