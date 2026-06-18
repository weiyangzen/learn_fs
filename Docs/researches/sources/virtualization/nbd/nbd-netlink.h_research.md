# File Research: sources/virtualization/nbd/nbd-netlink.h

Local copy of the Linux NBD generic netlink UAPI definitions.

It defines family name/version/multicast group name and enum values for NBD attributes, nested device-list attributes, nested socket attributes, and netlink commands: connect, disconnect, reconfigure, link-dead, and status.

`nbd-client.c` uses these definitions when compiled with libnl support to configure NBD devices without the older ioctl flow.
