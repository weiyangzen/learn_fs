# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/bos.h

## Role

Defines illumos USB Binary Object Store (BOS) descriptor layouts and parsed capability records for USB 3.x hub/framework use.

## Key Interfaces

- Defines BOS device capability type constants: WUSB, USB 2.0 extension, SuperSpeed, container ID, platform, Power Delivery, SuperSpeedPlus, precision time, and related values.
- Defines packed-size constants for wire descriptors so parser code can validate descriptor lengths independent of compiler padding.
- Provides C layouts for BOS header, generic device capability descriptor, USB 2.0 extension, SuperSpeed USB, container ID, platform capability, SuperSpeedPlus capability, and precision-time capability.
- Provides bitfield extraction macros for USB 2.0 LPM, SuperSpeed speed support, SuperSpeedPlus attribute counts, lane/functionality fields, sublink-speed attributes, lane speed exponent/protocol/type, and link speed mantissa.
- Defines `usb_bos_t`, an internal parsed representation with length, type, and a union of known capability structures plus a 256-byte raw fallback.

## Design Notes

The comments explicitly state this is separated from primary USBAI headers because BOS handling is currently private to hub/framework functionality, not normal client drivers.

## Risk Notes

Descriptor length constants and bitfield macros must match the USB 3.1 specification. Incorrect sizes or masks can cause BOS parsing to misclassify capability data or overrun/underrun variable-length descriptors.
