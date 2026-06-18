# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/genconsole.h

## Role

Declares generic USB console input/output support used to hand USB keyboard/output state between HID/USBA and lower host-controller layers for OBP/polled console mode.

## Key Interfaces

- Defines opaque `usb_console_info_t` and lower-layer `usb_console_info_private_t`.
- Defines `usb_console_info_impl_t` with the target device `dev_info_t` and lower-layer private state pointer.
- Declares input lifecycle: `usb_console_input_init`, `usb_console_input_fini`, `usb_console_input_enter`, `usb_console_read`, and `usb_console_input_exit`.
- Declares output lifecycle: `usb_console_output_init`, `usb_console_output_fini`, `usb_console_output_enter`, `usb_console_write`, and `usb_console_output_exit`.

## Design Notes

Input/output enter and exit calls are responsible for preserving and restoring controller state when OBP takes control of the USB keyboard or console output path.

## Risk Notes

These interfaces are sensitive to polled-mode state transitions. Failure to save/restore lower controller state can leave normal interrupt-driven USB operation inconsistent after console/OBP use.
