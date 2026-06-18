# sources/test-tools/strace/bundled/linux/include/uapi/linux/seg6_genl.h

## Purpose

Defines the generic netlink family ABI for IPv6 Segment Routing (`SEG6`). strace uses it to decode generic netlink family name/version, commands, and attributes.

## Important APIs, Types, and Dependencies

There are no include dependencies. Exports are `SEG6_GENL_NAME`, `SEG6_GENL_VERSION`, attributes `SEG6_ATTR_DST`, `DSTLEN`, `HMACKEYID`, `SECRET`, `SECRETLEN`, `ALGID`, and `HMACINFO`, and commands `SEG6_CMD_SETHMAC`, `DUMPHMAC`, `SET_TUNSRC`, and `GET_TUNSRC`.

## Control Flow, State, and Integration

The header is declarative. Runtime flow is userspace sending generic-netlink requests to configure or dump SRv6 HMAC settings and tunnel source address state. Kernel state persists in the network namespace SRv6 configuration.

## Risks and Test Signals

Risks are simple but important: generic netlink decoders must distinguish attributes from commands, preserve unknown attrs, and handle secret material carefully when displaying payloads. Test signals include named family, command, and attribute output for `SEG6`.
