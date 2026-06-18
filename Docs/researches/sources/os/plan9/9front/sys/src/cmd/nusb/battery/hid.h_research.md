# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/battery/hid.h

HID constants used by the USB battery driver.

Key elements:
- Defines thread stack size and an unused joystick-style `Maxaxes` constant.
- Defines HID class requests: `Getreport`, `Setreport`, `Getproto`, `Setproto`.
- Defines boot/report protocol constants.
- Defines report type value for output reports.
- Defines HID report descriptor item tags for main, global, and local items.
- Defines main item flag bits for data/constant, array/variable, absolute/relative, wrap, linearity, preference, and null state.

Notable behavior:
- The header is generic HID parsing support, despite the top comment mentioning joystick constants.
- Battery code uses the item tags and flags for report descriptor parsing.
