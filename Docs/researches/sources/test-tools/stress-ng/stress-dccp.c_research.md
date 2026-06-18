# sources/test-tools/stress-ng/stress-dccp.c

## Purpose
This stressor exercises Datagram Congestion Control Protocol socket I/O. It forks a client and server pair, binds a reserved port, accepts DCCP connections, sends variable-sized buffers using `send`, `sendmsg`, or optional `sendmmsg`, and measures message throughput.

## Important APIs, Types, And Functions
`stress_dccp_options()` exposes send mode names. `stress_dccp_client()` creates a DCCP socket, builds an interface/domain-specific address, retries connect, and receives until EOF or stop. `stress_dccp_server()` creates, binds, listens, accepts, sends message batches, probes socket state with `getsockname()`, `getsockopt(SO_SNDBUF)`, `getpeername()`, and optional `SIOCOUTQ`, then records throughput. `stress_dccp()` handles option parsing, interface validation, port reservation, fork, affinity, scheduling, and cleanup.

## Control Flow
The worker installs a SIGCHLD handler, reads interface, port, domain, send mode, and message-count options, validates the requested interface, reserves an instance-specific port, synchronizes, then forks. The child becomes the client, moves near the parent's CPU, applies scheduler settings, and receives data. The parent runs the server loop. The server accepts connections and sends up to `dccp-msgs` chunks per connection according to the selected method, incrementing bogo operations after send batches. On stop it closes sockets, reports messages per second, kills the client, and releases the port.

## State And Persistence
State is transient network/socket state plus a reserved port range in stress-ng's port manager. Optional AF_UNIX cleanup is present, though the domain mask defaults to IPv4/IPv6. No data is persisted beyond kernel socket buffers and metrics.

## Dependencies And Integration Points
The file depends on `SOCK_DCCP` and `IPPROTO_DCCP`, stress-ng network address/port/interface helpers, affinity and scheduler helpers, signal handling, kill helpers, and optional `sendmmsg()` and Linux socket ioctl support. Without DCCP definitions it registers an unimplemented stressor.

## Risks
DCCP is often disabled or unsupported by kernel configuration, so socket creation may skip as not implemented. Network namespace, firewall, or interface configuration can make connect/bind fail. The retry loop can delay failure by about one second. Send mode behavior differs by kernel, and large `dccp-msgs` values can hold a worker in connection I/O for a long time. Port reservation and release must remain paired.

## Test Signals
Signals include graceful skip on unsupported DCCP, successful loopback IPv4/IPv6 runs, correct interface fallback to loopback, port release after interruption, throughput metrics, and coverage of `send`, `sendmsg`, and `sendmmsg` where compiled.
