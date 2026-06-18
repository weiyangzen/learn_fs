<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/client.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/client.go

This file creates lightweight client identities for multiclient robustness tests. `Client` contains a UUID-backed `ID` and a petname `Name`; context helpers attach a client to a `context.Context` under an unexported key.

The important APIs are `newClient`, `NewClientContext`, `NewClientContexts`, and `UnwrapContext`. Control flow is simple: tests create one or more client contexts, then multiclient file writers and snapshotters use `UnwrapContext` to select or lazily create per-client resources.

State is carried through context values rather than globals. Dependencies are `github.com/google/uuid` and `golang-petname`. Risks include nil clients when callers forget to wrap contexts, and context values being invisible to unrelated contexts. Test signals appear in multiclient harness `RunN` and snapshotter/filewriter wrappers that return `ErrKeyNotFound` on missing clients.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/client.go -->
