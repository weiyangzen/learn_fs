# sources/user-network-fs/rclone/backend/union/policy/epff.go

Purpose: existing-path-first-found policy. It selects one upstream where a path exists.

Important APIs: `EpFF`, registered as `epff`; helper `epff`; action/create/search and entry variants.

Control flow/state: launches one goroutine per upstream, sends found-or-nil candidates over a channel, and returns the first non-nil result received. Action filters writable, create filters creatable and probes parent path, search probes exact path.

Dependencies/integration: `context`, `path`, `upstream`, `fs`; embedded by first-found and several existing-path policies.

Risks/test signals: due to concurrent probes, "first found" is first response, not strictly first configured upstream. Coverage is mainly indirect.
