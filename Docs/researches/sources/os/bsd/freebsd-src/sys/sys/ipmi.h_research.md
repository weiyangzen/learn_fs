# File Research: sources/os/bsd/freebsd-src/sys/sys/ipmi.h

Defines the IPMI character-device ioctl ABI and protocol constants. It includes maximum address/RX sizes, channel/address defaults, address type constants, receive types, net function/command identifiers, chassis controls, device capability bits, message flags, and watchdog settings.

Ioctls use magic `'i'` and cover receiving messages, sending commands, registering/unregistering command handlers, event command control, and local BMC address/LUN get/set. Message structures are `ipmi_msg`, `ipmi_req`, `ipmi_recv`, `ipmi_cmdspec`, and address variants for generic, system-interface, and IPMB addresses.

On amd64, 32-bit compatibility command numbers and pointer-truncated structs are provided for `ipmi_recv32`, `ipmi_req32`, and `ipmi_msg32`.
