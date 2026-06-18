# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/generate_unions.go

## Purpose

`generate_unions.go` contains special-case union selection for strace arguments whose syzkaller descriptions cannot be inferred by a simple first-field fallback. It primarily maps socket address and interface request traces into the correct syzkaller union arm.

## Important APIs, Types, and Functions

The methods are `(*context).genSockaddrStorage`, `(*context).genSockaddrNetlink`, and `(*context).genIfrIfru`. They use `prog.UnionType`, `prog.MakeUnionArg`, `parser.GroupType`, `parser.Constant`, `ctx.target.ConstMap`, and recursive `ctx.genArg`.

## Control Flow

`genUnionArg` in `proggen.go` dispatches here for union type names `sockaddr_storage`, `sockaddr_nl`, and `ifr_ifru`. `genSockaddrStorage` reads the first parsed group element as an address family and chooses arms such as `in6`, `in`, `un`, `nl`, `nfc`, or `ll`. `genSockaddrNetlink` inspects the netlink PID to choose user, kernel, or unspecified arms. `genIfrIfru` chooses an alternate field when strace produced a plain constant.

## State and Persistence Behavior

The functions build local field-name-to-index maps on each call and do not persist state. They depend on the context's target constant map and current conversion context.

## Dependencies and Integration Points

They integrate tightly with Linux syscall descriptions and `tools/syz-trace2syz/parser` IR shapes. They are called only from `proggen` union generation and must track syzkaller union field names.

## Risks and Test Signals

The logic assumes parsed groups are non-empty and the first element is a constant; malformed or unexpected traces can trigger fatal logging. Field-name drift in syscall descriptions would silently select the zero arm or panic through bad assumptions. Test signals include socket connect/bind/sendto traces for IPv4, IPv6, UNIX, netlink, NFC, packet sockets, and ioctl ifreq variants.
