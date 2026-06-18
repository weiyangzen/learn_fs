# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/joy/hid.h

This header defines HID constants used by the USB joystick driver. It includes thread stack size, joystick and Xbox 360 class/subclass/protocol identifiers, maximum supported axes, HID class request codes, protocol values, output report selector, report descriptor item tags, and main-item flag bits.

The item-tag and flag constants mirror the generic HID report parser in `joy.c`: main items (`Input`, `Output`, `Collection`, `Feature`), global items (`Usage Page`, logical/physical bounds, report size/id/count), local items (`Usage`, usage ranges, designator/string fields), delimiter handling, and data/constant, variable/array, absolute/relative flags.
