# sources/user-network-fs/rclone/backend/union/policy/policy.go

Purpose: policy interface, registry, and shared filtering/lookup helpers for union branch selection.

Important APIs: `Policy` with Action/Create/Search and entry variants; `registerPolicy`, `Get`, `filterRO`, `filterROEntries`, `filterNC`, `filterNCEntries`, `parentDir`, `clean`, and `findEntry`.

Control flow/state: individual policy `init` functions populate a lower-case global registry. `findEntry` lists a parent directory, handles root specially, and compares remote names using backend case-sensitivity.

Dependencies/integration: `context`, `fmt`, `path`, `strings`, `time`, `upstream`, `fs`. `union.NewFs` resolves configured policy names through `Get`.

Risks/test signals: no collision protection in registry; `findEntry` lookup cost/correctness depends on backend listing behavior. Exercised by all union policy tests.
