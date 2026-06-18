## sources/test-tools/syzkaller/syz-hub/hub_test.go

`TestAuth` validates `Hub.checkManager` for static keys. It covers missing client/key, wrong key, wrong client's key, exact manager name, prefixed manager name, empty manager defaulting to client, and manager names without the client prefix.

This is a focused auth test. It does not cover OAuth-token keys, RPC `Connect`/`Sync`, state persistence, or HTTP behavior.
