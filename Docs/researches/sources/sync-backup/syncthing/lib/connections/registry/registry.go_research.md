## sources/sync-backup/syncthing/lib/connections/registry/registry.go

Purpose: Tracks listener-owned reusable connection objects by scheme so outbound dials can reuse local listen ports/transports for better NAT traversal.

Important APIs/types/functions: `Registry` holds `available map[string][]interface{}` guarded by `sync.Mutex`. `New`, `Register`, `Unregister`, and `Get` are the public API.

Control flow: `Register` appends items under a scheme. `Unregister` removes the first matching item by interface equality. `Get` scans registered schemes whose key is a prefix of the requested scheme, evaluates a caller-supplied preferred predicate, and picks the first available or a preferred item, breaking preferred ties toward shorter scheme names.

State and persistence: Process-local mutable registry only.

Dependencies and integration points: Uses `sliceutil.RemoveAndZero`. TCP listeners register `*net.TCPAddr`; QUIC listeners register `*quic.Transport`; TCP/QUIC dialers query the registry.

Risks: Uses `interface{}` and equality, so only comparable values can be unregistered safely. Prefix matching is intentional but broad; new schemes need care to avoid accidental compatibility.

Test signals: `registry_test.go` covers empty lookup, prefix compatibility, unregister semantics, duplicates, short-scheme preference, and a benchmark.
