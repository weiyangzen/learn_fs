# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/lib/dump.c

This file provides USB debug formatting and allocation helpers. It defines the global `usbdebug`, endpoint direction/type names, USB class names, and device-state strings.

`classname()` maps USB class codes to readable names, including common standard classes and several special class values. `Ufmt()` is the `%U` formatter for `Dev *`: it prints endpoint path, device class/subclass/protocol, vendor/product ids, reference count, vendor/product/serial strings, configurations, interfaces, endpoints, and raw device-specific descriptors. Helper routines format interfaces, endpoints, and configurations.

The file also defines `estrdup()` and `emallocz()`, fatal-on-failure wrappers used throughout the nusb code. These set malloc tags for debugging and match Plan 9 style by aborting on allocation failure instead of returning null.
