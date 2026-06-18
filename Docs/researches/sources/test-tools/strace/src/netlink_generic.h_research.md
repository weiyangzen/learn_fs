<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_generic.h -->
# sources/test-tools/strace/src/netlink_generic.h

Purpose: declares the generic netlink decoder signature and exported `nlctrl` decoder.

Important APIs/types/functions: `DECL_NETLINK_GENERIC_DECODER` macro and `decode_nlctrl` declaration.

Control flow: no runtime flow; the macro standardizes generic decoder prototypes that accept `struct genlmsghdr`, payload address, and payload length.

State and persistence behavior: no state.

Dependencies and integration points: includes `netlink.h` and `<linux/genetlink.h>`; consumed by `netlink_generic.c` and `netlink_nlctrl.c`.

Risks: signature drift would break generic family decoder registration. The macro hides the exact prototype, so compiler errors are the main guard.

Test signals: build coverage for every `DECL_NETLINK_GENERIC_DECODER` implementation and generic netlink dispatch tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_generic.h -->
