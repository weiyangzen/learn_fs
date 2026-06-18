# sources/test-tools/syzkaller/pkg/config/merge.go

Purpose: Recursive JSON object merge and patch helpers for syzkaller configs, especially when raw JSON subdocuments should be merged rather than replaced wholesale.

Important APIs/types/functions: `MergeJSONs`, `PatchJSON`, `parseFragment`, and `mergeRecursive`.

Control flow: `MergeJSONs` parses both JSON fragments and marshals the recursive merge result. `PatchJSON` parses the left JSON and merges a Go map patch. `parseFragment` treats empty input as nil. `mergeRecursive` returns the non-nil side when one side is nil, replaces non-map values with the right side, and recursively merges `map[string]any` values.

State and persistence behavior: Stateless pure byte/map transformation. Output JSON is compact marshaled JSON.

Dependencies/integration points: Used when layering config fragments or applying structured patches.

Risks: Arrays and scalar values are replaced, not merged. Number types become `float64` through `encoding/json` generic unmarshalling. Map iteration is normalized by `json.Marshal` for deterministic key order in tests.

Test signals: `merge_test.go` covers shallow merge, nested merge, empty-right preservation, and map patch replacement/creation.
