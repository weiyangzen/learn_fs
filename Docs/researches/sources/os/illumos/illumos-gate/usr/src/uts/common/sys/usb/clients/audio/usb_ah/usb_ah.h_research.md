# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_ah/usb_ah.h

## Purpose
USB audio HID helper state header for audio button/report handling.

## Main Interfaces
- Defines report indexes `USB_AH_INPUT_RPT`, `USB_AH_OUTPUT_RPT`, and `USB_AH_FEATURE_RPT`.
- Defines state flags `USB_AH_OPEN` and `USB_AH_QWAIT`.
- Defines `usb_ah_button_descr_t`, `usb_ah_rpt_t`, and `usb_ah_state_t`.
- `usb_ah_state_t` tracks STREAMS queues, report data, USB pipe/request state, mutex/CV synchronization, and HID report descriptors.
- Defines `USB_AH_TIMEOUT`.

## Dependencies And Relationships
Includes `sys/stream.h`. Used by the USB audio HID client that handles hardware audio buttons and related HID reports.

## Research Notes
The state includes a small fixed report array for input, output, and feature reports, reflecting the narrow HID usage in audio controls.
