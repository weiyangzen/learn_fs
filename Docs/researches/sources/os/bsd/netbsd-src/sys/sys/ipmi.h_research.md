# File Research: sources/os/bsd/netbsd-src/sys/sys/ipmi.h

Defines the user/kernel ioctl ABI for IPMI device messaging. It declares IPMI address limits, BMC defaults, address type constants, message/request/receive structures, command registration structures, address variants, and ioctl commands for send, receive, register/unregister, event enablement, address, and LUN access.

The ABI uses embedded user pointers for message data and addresses, so ioctl handlers must validate lengths and copy buffers carefully. Compatibility risk is high for structure layout and command numbers because IPMI tooling expects stable Linux-like semantics.
