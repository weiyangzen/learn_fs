# sources/user-network-fs/go-nfs/server.go

## Purpose

`server.go` defines the main NFS server type, the global RPC handler registry, connection acceptance loop, per-connection construction, handler lookup, and convenience `Serve` function. It is the network entry point for serving NFS requests over a `net.Listener`.

## Important APIs, Types, and Functions

`Server` embeds the user `Handler`, stores an 8-byte write verifier `ID`, and optionally carries a base `context.Context`. `HandleFunc` is the procedure callback signature. `RegisterMessageHandler(protocol, proc, handler)` registers global dispatch callbacks by `(protocol, proc)`. `(*Server).Serve(l net.Listener)` accepts connections and launches `conn.serve`. `(*Server).handlerFor(prog, proc)` resolves registered callbacks. Top-level `Serve(l, handler)` mirrors `http.Serve`.

## Control Flow

`Server.Serve` closes the listener on return, selects `context.Background()` unless `s.Context` is set, initializes `s.ID` from `crypto/rand` if all zeros, and then loops on `Accept`. Temporary timeout errors use exponential backoff from 5 ms up to 1 second before retrying. Non-temporary accept errors stop the server. Successful accepts reset backoff, wrap the `net.Conn` in a `conn` via `newConn`, and serve it in a goroutine with the base context.

## State and Persistence Behavior

The server mutates `s.ID` once per server lifetime when it starts, and uses it as the NFS write verifier in write responses. `registeredHandlers` is package-global mutable state shared by all server instances. Connections are served concurrently in goroutines. No on-disk persistence is used.

## Dependencies and Integration Points

This file integrates with lower-level `conn` request parsing and response writing code elsewhere in the package, all NFS and mount procedure registrations, the user-supplied filesystem `Handler`, and the write handler's verifier emission. It uses Go `net`, `context`, `crypto/rand`, and timeout semantics.

## Risks and Edge Cases

`registeredHandlers` is a global map without synchronization; concurrent registration or lookup can race, and duplicate checks are O(n). Handler state is global rather than server-scoped, so tests or embedders cannot easily isolate registries. The accept loop does not stop on context cancellation; context is only passed to connection handlers. `rand.Reader.Read` is used directly instead of `io.ReadFull`, so a short read could leave a partially random verifier without error if ever returned by the reader. Listener close on `Serve` return can surprise callers that expect ownership to remain outside.

## Test Signals

Existing integration tests start `nfs.Serve` on a local TCP listener and verify mount and file operations, which exercises ID generation, accept, connection goroutines, and handler dispatch. Additional tests should cover duplicate registration, timeout accept behavior with a fake listener, server-specific context propagation, registry race behavior under `go test -race`, and write verifier initialization.
