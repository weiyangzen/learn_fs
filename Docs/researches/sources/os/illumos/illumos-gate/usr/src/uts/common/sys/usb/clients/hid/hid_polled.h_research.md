# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hid_polled.h

## Purpose
USB HID polled-input callback interface for low-level input polling.

## Main Interfaces
- Defines commands `HID_OPEN_POLLED_INPUT` and `HID_CLOSE_POLLED_INPUT`.
- Defines interface version `HID_POLLED_INPUT_V0`.
- Defines opaque `hid_polled_handle_t`.
- Defines `hid_polled_input_callback_t` with version, handle, argument, and callbacks for enter, exit, and input polling.

## Dependencies And Relationships
Used by HID keyboard/mouse paths that need polled input, such as console/debugger or early/low-level input contexts.

## Research Notes
The interface is callback-based and explicitly versioned, allowing HID providers to expose polling without publishing internal driver state.
