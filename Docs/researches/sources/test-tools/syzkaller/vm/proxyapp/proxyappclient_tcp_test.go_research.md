# sources/test-tools/syzkaller/vm/proxyapp/proxyappclient_tcp_test.go

## Purpose

`proxyappclient_tcp_test.go` tests proxyapp's TCP and TLS JSON-RPC connection modes and reconnection behavior when server connections are closed.

## Important APIs, Types, and Functions

Key helpers are `testTCPEnv`, `testTCPEnvTLS`, `proxyAppServerTCPFixture`, `proxyAppServerTCPFixtureTLS`, `makeMockProxyAppServerWithListener`, `makeMockProxyAppServer`, and `makeMockProxyAppServerTLS`. Tests include successful TCP construction, successful TLS construction with generated certs, and lost-connection reinitialization scenarios.

## Control Flow

The tests create a loopback listener, register a mock `ProxyVM` service over JSON-RPC, build a proxyapp environment pointing at the listener, and call `ctor`. TLS tests generate a self-signed localhost certificate and pass it through `server_tls_cert`. Lost-connection tests close accepted connections and assert the client reconnects or remains unable to initialize depending on server behavior.

## State and Persistence Behavior

The tests create local listeners, accepted TCP/TLS connections, generated certificate files where needed, and in-memory mock state. Cleanup is coordinated by the test context and connection close helper.

## Dependencies and Integration Points

They exercise `initNetworkRPCClient`, TLS root pool handling, URI parsing, log polling, supervisor reconnect behavior, and `pool.proxy` state transitions.

## Risks and Test Signals

The listener goroutine panics on accept errors, so cleanup ordering matters. Generated cert validity and DNS name must match `localhost`. Strong signals are successful non-TLS and TLS pool creation, reconnect after closed connections, and nil proxy state while reinit cannot complete.
