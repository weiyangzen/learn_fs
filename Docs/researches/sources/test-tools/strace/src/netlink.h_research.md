<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink.h -->
# sources/test-tools/strace/src/netlink.h

Purpose: shared netlink header helpers and normalized header-length macros for netlink decoders.

Important APIs/types/functions: redefines `NLMSG_HDRLEN` and `NLA_HDRLEN` as unsigned aligned lengths and provides inline `is_nlmsg_ok`.

Control flow: `is_nlmsg_ok` validates that a buffer contains a full `struct nlmsghdr`, that `nlmsg_len` is at least the header size, and that the caller-provided length covers the message.

State and persistence behavior: no runtime state; it contributes constants and inline validation.

Dependencies and integration points: includes `<stdbool.h>`, `<sys/socket.h>`, and `<linux/netlink.h>`; used by netlink and nlattr decoders that need consistent alignment semantics.

Risks: changes to alignment macros or validation rules affect all netlink family decoders. The helper validates one message only and does not check multi-message overflow.

Test signals: malformed netlink header unit cases should exercise short buffers, too-small `nlmsg_len`, exact-length messages, and oversized messages.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink.h -->
