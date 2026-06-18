# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipmi.h

This header defines ioctl ABI and message/address structures for IPMI.

Key definitions:
- Limits and defaults: `IPMI_MAX_ADDR_SIZE`, `IPMI_MAX_RX`, BMC slave address/channel, BMC SMS LUN.
- Address types: system interface, IPMB, IPMB broadcast.
- Ioctl magic and commands:
  - Receive message, receive truncated message, send command.
  - Register/unregister command.
  - Set/get event command behavior.
  - Set/get own address and LUN.
- Receive types: response, async event, command.
- IPMI app netfn/command constants for device ID, flags, get/send message, channel info, watchdog reset/set/get.
- Watchdog timer flags/actions.

Structures:
- `ipmi_msg`, `ipmi_req`, `ipmi_recv`, `ipmi_cmdspec`.
- Generic and specific address structures: `ipmi_addr`, `ipmi_system_interface_addr`, `ipmi_ipmb_addr`.
- Under `_KERNEL`, 32-bit ioctl-compatible forms: `ipmi_msg32`, `ipmi_req32`, `ipmi_recv32`, and 32-bit ioctl command variants.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

License note:
- Carries BSD-style copyright from IronPort/FreeBSD plus Joyent copyright.

Relevance:
- Platform management interface. Indirect relevance to storage systems through watchdogs/platform control, not filesystem logic.
