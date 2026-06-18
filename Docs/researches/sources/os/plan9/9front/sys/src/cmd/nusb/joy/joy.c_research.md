# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/joy/joy.c

This file implements a USB HID game-controller reader that prints joystick events to standard output. It opens an interrupt IN endpoint, obtains or supplies a HID report descriptor, parses incoming reports, tracks up to six axes and 64 buttons, and emits textual `axis`, `down`, and `up` lines for changed state.

The HID report parser is a compact recursive parser over HID short/long items. `repparse1()` maintains global and local item state, expands usage ranges, handles collections and push/pop, and calls a callback for each logical field in Input/Output/Feature items. `getbits()` extracts arbitrary bit fields from reports, and `signext()` handles signed fields.

`joyparse()` consumes Input fields only. It honors report ids, applies signed conversion and a configurable deadband, maps desktop usages X/Y/Z/Rx/Ry/Rz to axes, and maps button-page usages to a 64-bit button mask. `joywork()` reads reports, parses them, prints axis changes and button transitions, and retries transient read errors before treating the device as fatal.

The driver includes controller quirks. A PS3 controller is enabled through a feature-report request. Xbox 360 and compatible controllers often lack a HID descriptor, so `xbox360()` injects a synthetic report descriptor and sends an LED command. Some Shanwan-compatible devices receive vendor reads before the synthetic descriptor is installed.

`threadmain()` accepts debug and deadband options, selects a suitable interrupt IN endpoint matching generic joystick or Xbox 360 CSP values, and starts the reader.
