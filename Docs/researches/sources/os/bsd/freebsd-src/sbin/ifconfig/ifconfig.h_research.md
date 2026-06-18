# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig.h

`ifconfig.h` defines the shared internal API for `ifconfig` modules. It declares the context object, command handler signatures, command registration macros, address-family switch table, parsed argument structure, option registration, global formatting variables, and cross-module helper functions.

The command table supports fixed integer parameters, one argument, two arguments, optional argument, string parameter, vector arguments, and clone-only commands. The address-family table abstracts status output, address parsing/copying, prefix parsing, post-processing, VHID propagation, kernel execution, add/delete request storage, tunnel status/setup, and ioctl/netlink differences.

The header also declares netlink entry points when available, clone default callback registration, SFP/media hooks, common status/format helpers, and sockaddr cast helpers. Its compile-time `WITHOUT_NETLINK` macros change callback signatures and mark netlink-only parameters as used or unused.
