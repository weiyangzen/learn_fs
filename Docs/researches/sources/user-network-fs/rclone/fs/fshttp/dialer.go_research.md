<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/dialer.go -->
# sources/user-network-fs/rclone/fs/fshttp/dialer.go

## Purpose
Builds rclone's HTTP/network dialer with connect timeout, idle timeout, local bind address, DSCP traffic class, and transport bandwidth accounting.

## Important APIs, Types, And Control Flow
`NewDialer` reads `fs.ConfigInfo` for connect timeout, IO timeout, bind address, and traffic class. `DialContext` forces tcp4/tcp6 when binding unspecified IPv4/IPv6 addresses, dials, applies IPv4 TOS or IPv6 traffic class with one-time warnings, and wraps the connection in `timeoutConn`. `timeoutConn` refreshes deadlines after successful reads/writes and accounts transport RX/TX through the accounting token bucket.

## State And Persistence
Dialer instances hold timeout/tclass config. Package `sync.Once` values suppress repeated DSCP warnings. No persistent files.

## Dependencies And Integration Points
Used by fshttp transports and clients. Integrates net.Dialer, x/net ipv4/ipv6 socket options, global config, logging, and accounting bandwidth limits.

## Risks And Test Signals
DSCP support varies by OS and can fail silently on Windows IPv4. Deadline updates only occur after nonzero successful IO. Tests in this subset target dump behavior, not dialer sockets directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/dialer.go -->
