# sources/test-tools/syzkaller/vm/proxyapp/init.go

## Purpose

`init.go` defines configuration parsing and backend registration for the experimental proxyapp VM backend, which delegates VM operations to an external plugin over JSON-RPC.

## Important APIs, Types, and Functions

Key pieces are `makeDefaultParams`, `init`, `proxyAppParams`, `osutilCommandContext`, `subProcessCmd`, `Config`, `parseConfig`, and `URIParseErr`. Config fields include command, RPC server URI, security mode, server TLS certificate, transfer-file-content mode, and opaque plugin config.

## Control Flow

Registration wires `proxyapp` to `ctor(makeDefaultParams(), env)`. `parseConfig` loads JSON, requires either `cmd` or `rpc_server_uri`, validates URI shape when supplied, and returns config. `URIParseErr` prepends `http://` for parsing, then requires host:port without scheme decorations.

## State and Persistence Behavior

The file itself creates no persistent state. `proxyAppParams` allows tests to inject command runners, retry delay, and log output.

## Dependencies and Integration Points

It depends on `config.LoadData`, `osutil.CommandContext`, `vmimpl.Register`, and the client implementation in `proxyappclient.go`.

## Risks and Test Signals

URI validation permits only simple host:port strings. Mutual TLS is accepted at config level but implemented as an error in client setup. `init_test.go` covers command/URI combinations, bad URI formats, and opaque config preservation.
