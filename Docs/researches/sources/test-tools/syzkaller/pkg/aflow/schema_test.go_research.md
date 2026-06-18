# sources/test-tools/syzkaller/pkg/aflow/schema_test.go

Purpose: verifies schema type validation and `convertFromMap` behavior for tool and non-tool error modes.

Important APIs/functions: `TestSchema`, `TestConvertFromMap`, and helper `testConvertFromMap`. The tests call `schemaFor` and `convertFromMap` with a broad set of struct shapes.

Control flow: `TestSchema` checks non-struct rejection, missing `jsonschema` tag errors, and successful tagged struct schema generation. `TestConvertFromMap` covers integer and uint conversion from JSON float64, strings, `json.RawMessage`, missing fields, wrong types, truncating floats, unused strict fields, `omitempty`, slices of structs and strings, nested structs, pointer numeric fields, slice item errors, nil slice entries, pointer slice nil allowance, and `time.Time` unmarshaling.

State and persistence: no persistent state. Each case creates input maps and expected typed outputs.

Dependencies and integration: imports `encoding/json`, `fmt`, `testing`, `time`, `jsonschema`, and testify. It locks down the conversion behavior consumed by actions, tools, MCP handlers, and LLM tool-call argument parsing.

Risks and test signals: the strongest signal is paired tool/non-tool error text, because tool mode must produce LLM-facing `BadCallError` messages while internal mode returns ordinary errors. Changes to Go reflection formatting or map ordering may require careful fixture updates.
