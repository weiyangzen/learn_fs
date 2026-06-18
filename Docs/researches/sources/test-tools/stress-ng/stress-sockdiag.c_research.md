# sources/test-tools/stress-ng/stress-sockdiag.c

## Purpose

`stress-sockdiag.c` implements `sockdiag`, a Linux netlink stressor that sends `NETLINK_SOCK_DIAG` dump requests and parses returned socket diagnostic attributes. It focuses on kernel sock_diag request/response paths, especially Unix socket diagnostic messages, while cycling request families and `udiag_show` masks.

## Important APIs, Types, and Functions

- `stress_sockdiag_request_t` combines `nlmsghdr` and `unix_diag_req` into the request payload sent to netlink.
- `sockdiag_send()` fills the diagnostic family and `udiag_show` mask, sends requests via `sendmsg()`, cycles families, and returns positive/zero/negative status for sent/stopped/error.
- `stress_sockdiag_parse()` validates response length, iterates `rtattr` attributes with `RTA_OK`/`RTA_NEXT`, and adds the attribute count to bogo operations.
- `sockdiag_recv()` reads netlink responses with `recvmsg()`, validates `nlmsghdr` entries, handles `NLMSG_DONE` and `NLMSG_ERROR`, and dispatches diagnostic payloads to the parser.
- `stress_sockdiag()` repeatedly opens `socket(AF_NETLINK, SOCK_RAW, NETLINK_SOCK_DIAG)`, sends one query, receives the dump, closes the socket, and loops while the stressor continues.

## Control Flow

After the synchronization barrier, each loop opens a raw netlink sock_diag socket. If the protocol is unsupported, instance zero reports a skip and returns `EXIT_NOT_IMPLEMENTED`. Otherwise `sockdiag_send()` prepares a `SOCK_DIAG_BY_FAMILY` request with `NLM_F_REQUEST | NLM_F_DUMP`, chooses a family from a compiled list, tries `udiag_show` bits one at a time, and finally tries all bits. The first successful `sendmsg()` returns to the caller.

The receive side loops through netlink messages in a static aligned buffer. It rejects malformed messages, stops on `NLMSG_DONE`, treats `NLMSG_ERROR` or unexpected message types as errors, and otherwise counts response attributes. The entry point ignores receive errors but treats send failures as stressor failure. Each outer iteration closes the netlink fd.

## State and Persistence Behavior

The stressor keeps static request, address, iovec, message, family index, and receive buffer state inside helper functions. These are process-local and reused across loop iterations. It creates no files and no persistent kernel objects beyond transient netlink sockets.

## Dependencies and Integration Points

This file is Linux-only and requires `linux/netlink.h`, `linux/rtnetlink.h`, `linux/sock_diag.h`, and `linux/unix_diag.h`. It uses stress-ng state transitions, continue checks, bogo accounting, and logging. The exported stressor is `CLASS_NETWORK | CLASS_OS`, `VERIFY_ALWAYS`; unsupported builds export `stress_unimplemented`.

## Risks and Edge Cases

The request structure is Unix-diag-specific but the family field is varied across many address families; unsupported family/show combinations are expected to fail. Static mutable request state makes the helper simple but not reentrant. `sockdiag_recv()` treats unexpected netlink payloads as failures, which is appropriate for verification but can be sensitive to kernel ABI changes. The code handles `EINTR` during receive and send retry loops but does not deeply inspect netlink error payloads.

## Test Signals

On Linux kernels with `NETLINK_SOCK_DIAG`, a short run should open netlink sockets, send requests, parse attributes, and increment bogo counts. On kernels lacking support it should print a skip and return not implemented/no-resource rather than fail. Build testing should cover missing header paths to validate the unimplemented branch.
