# sources/test-tools/syzkaller/pkg/aflow/schema.go

Purpose: provides reflection-based schema validation, JSON schema generation, map-to-struct conversion, struct-to-map extraction, and field iteration helpers for aflow actions/tools.

Important APIs/functions: `schemaFor`, `uncheckedSchemaFor`, `checkSchemaType`, `mustSchemaFor`, `convertToMap`, `convertFromMap`, `convertFromMapReflect`, `setField`, `setSliceField`, `extractOutputs`, `foreachField`, and `foreachFieldOf`.

Control flow: schema generation requires a struct type and recursively enforces `jsonschema` descriptions on visible fields. Conversion clones the input map, walks exported visible fields, enforces required fields unless `omitempty`, optionally rejects unused fields in strict mode, and delegates each assignment to `setField`. `setField` handles pointer targets, `json.RawMessage`, JSON float-to-int conversion with truncation checks, exact type matches, `json.Unmarshaler` types such as `time.Time`, nested structs, and slices.

State and persistence: no durable state. The functions transform in-memory maps and structs; `extractOutputs` intentionally panics if state lacks required outputs after verification.

Dependencies and integration: depends on `encoding/json`, `reflect`, `maps`, `iter`, `strings`, and `github.com/google/jsonschema-go/jsonschema`. It underpins action/tool argument conversion, MCP schemas, LLM tool schemas, and test helpers.

Risks and test signals: risks include reflection panics on unsupported shapes, silent non-strict nested-field tolerance, JSON number precision/truncation, missing `jsonschema` tags, and nil handling in slices. `schema_test.go` exercises error wording and common conversion paths.
