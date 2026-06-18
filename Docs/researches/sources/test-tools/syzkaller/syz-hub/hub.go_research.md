## sources/test-tools/syzkaller/syz-hub/hub.go

`syz-hub` is an RPC/HTTP process that exchanges corpus programs and reproducers among syz-manager clients. `Config` defines HTTP/RPC/workdir and authorized clients. `Hub` holds a mutex, persistent `state.State`, client keys, and an auth endpoint.

`main` loads config, enables log caching, loads state, builds the client-key map, serves HTTP summary, starts hourly old-manager purging, and serves RPC as `Hub`. `Connect` authenticates manager identity then records manager metadata, supported calls, and initial corpus. `Sync` authenticates, applies added/deleted corpus entries, returns pending inputs, records incoming repros, and optionally returns a pending repro. Authentication supports static keys and OAuth magic expected subjects, and manager names must be empty or prefixed by client name.

State persists through `syz-hub/state`. Integration points are syz-manager `HubConnector`, HTTP dashboard, auth package, and rpctype RPC. Risks include one global mutex around potentially heavy state operations, generic "unauthorized manager" errors for all auth failures, and reliance on clients periodically reconnecting/purging. Tests cover static-key manager authentication.
