# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usbai.h

## Role

Primary public USB Architecture Interface (USBAI) header for illumos USB client drivers.

## Key Interfaces

- Defines USBAI version `2.1`, device states, return codes, callback flags, completion reasons, opaque pipe handles, opaque pointer type, and sleep/nosleep flags.
- Defines standard USB descriptor structures for device, qualifier, configuration, other-speed configuration, interface association, interface, endpoint, string, and SuperSpeed endpoint companion descriptors.
- Defines endpoint direction/type/synchronization/usage masks, packet-size masks, interval ranges, string length, and configuration attribute bits.
- Defines parsed descriptor-tree data structures: configuration, interface, alternate interface, endpoint, class/vendor-specific descriptor, parse levels, and `usb_client_dev_data_t`.
- Declares client registration, detach, descriptor tree free/print, descriptor parsing, endpoint lookup, string retrieval, address/interface/ownership utilities, and extended endpoint descriptor filling.
- Defines public pipe states and pipe policy, then declares pipe open/xopen/close/drain/reset/state/private-data APIs.
- Defines transfer request attributes and request structures/APIs for control, bulk, interrupt, and isochronous transfers.
- Defines setup/control request constants, descriptor type constants, standard request type/recipient masks, standard USB requests, feature selectors, and status bits.
- Declares wrapper helpers for synchronous control transfers, standard status/clear-feature/configuration/alternate-interface operations, max bulk size, current frame, and max isochronous packet count.
- Defines power management constants/masks/conversion macros, remote wakeup handling, PM component creation, hotplug callback registration, device reset levels, and `usb_reset_device()`.
- Defines project-private USB device capture registration callback types and APIs.
- Defines USB class, subclass, and protocol constants for audio, CDC, HID, printer, mass storage, hub, video, wireless, misc, application, and vendor-specific classes.

## Design Notes

This header is both a public driver contract and a detailed semantic specification. Its comments define legal state transitions, callback behavior, transfer queueing rules, polling rules, and blocking semantics.

## Risk Notes

This is ABI/API critical. Structure layouts, enum values, return codes, version checks, request semantics, and callback rules must remain compatible with existing USB drivers and HCD behavior.
