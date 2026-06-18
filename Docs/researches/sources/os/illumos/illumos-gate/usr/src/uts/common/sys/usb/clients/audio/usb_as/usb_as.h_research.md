# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_as/usb_as.h

## Purpose
USB audio streaming driver state header for playback/recording streams, alternate settings, isochronous requests, and stream power state.

## Main Interfaces
- Defines queue watermarks `USB_AS_HIWATER` and `USB_AS_LOWATER`.
- Defines `usb_as_alt_descr_t` for alternate interface/audio format metadata.
- Defines `usb_as_power_t` for power management state.
- Defines central `usb_as_state_t` with USB handles, interface descriptors, pipes, queues, transfer state, format state, taskq arguments, power state, and synchronization.
- Defines taskq argument `usb_as_tq_arg_t` and request wrapper `usb_as_req_t`.
- Defines default availability values, send-result values, stream states such as idle/active/paused/stop-polling, request counts, open/dismantling flags, buffer size, and minor number helpers.

## Dependencies And Relationships
Includes `sys/usb/usba/usbai_private.h`. Cooperates with `usb_ac.h` for control-driver coordination and `usb_mixer.h` for audio framework registration.

## Research Notes
The header models USB audio streaming around alternate interface descriptors and isochronous request management, with explicit play-pause and stop-polling states.
