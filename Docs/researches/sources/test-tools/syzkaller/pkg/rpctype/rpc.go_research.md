# sources/test-tools/syzkaller/pkg/rpctype/rpc.go

## Purpose

`rpc.go` is the older compressed `net/rpc` transport wrapper used by syzkaller components such as syz-manager and syz-hub.

## Important APIs, Types, And Control Flow

`RPCServer` wraps a TCP listener and `rpc.Server`; `NewRPCServer` listens and registers a named receiver; `Serve` accepts forever, enables TCP keepalive, wraps the connection with flate compression, and serves it in a goroutine. `RPCClient` wraps a TCP connection and `rpc.Client`; `NewRPCClient` dials with a three-minute timeout and compression; `Call` sets a ten-minute deadline around each RPC; `Close` closes the client. `flateConn` adapts `io.ReadWriteCloser` through `flate.Reader` and level-9 `flate.Writer`, flushing on every write and closing all layers.

## State, Dependencies, Integration, Risks, And Test Signals

State is the listener, TCP connection, RPC codec, and compression streams. Dependencies are Go `net/rpc`, `compress/flate`, TCP keepalive, and `pkg/log`. Risks include `Serve` never exiting on listener close because accept errors are only logged, unchecked TCP type assertions in `setupKeepAlive`, per-write flush overhead, and deadlines being unavailable on some platforms by comment. No tests are in this subset; integration with hub RPC call paths is the expected signal.
