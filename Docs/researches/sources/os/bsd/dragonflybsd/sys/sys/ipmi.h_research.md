# File Research: sources/os/bsd/dragonflybsd/sys/sys/ipmi.h

`ipmi.h` defines the IPMI user/kernel ioctl ABI and message structures. It includes `ioccom.h`.

The header defines address/data-size limits, BMC defaults, IPMI address types, ioctl command constants for receiving, sending, command registration, event command configuration, address get/set, and LUN get/set, plus receive types and common application command constants such as get device ID, get/clear message flags, watchdog commands, and watchdog action bits.

It declares `ipmi_msg`, `ipmi_req`, `ipmi_recv`, `ipmi_cmdspec`, generic/system-interface/IPMB address structures, and amd64 32-bit compatibility ioctl structures with 32-bit pointer fields. This is a pointer-bearing ioctl ABI, so compatibility and copyin/copyout handling are central to its consumers.
