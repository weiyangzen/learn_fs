# sources/user-network-fs/gcsfuse/tools/metrics-gen/main.go

Purpose: code generator that reads `metrics.yaml` and emits metric handle, noop metrics, OpenTelemetry metrics, and OTel metric tests from templates.

Important APIs/types/functions: schema structs `Metric`, `Attribute`, `AttrValuePair`, `AttrCombination`, `DistinctAttr`, `TemplateData`; name/unit helpers; `generateCombinations`; validators; `buildSwitches`; `findDistinctAttributes`; `main`; and `createFile`.

Control flow: reads YAML, validates uniqueness, sort order, metric fields, attribute fields, and constant-name collisions; normalizes attributes and values for deterministic generation; derives distinct string attribute types and all attribute combinations; executes four templates into the output directory.

State/persistence behavior: reads an input YAML file, creates the output directory, and writes generated Go files. It has no long-lived runtime state.

Dependencies/integration: depends on `text/template`, `gopkg.in/yaml.v3`, and local template files expected in the working directory.

Risks/test signals: templates are loaded by relative name, so the generator must run from the template directory or equivalent. Validators enforce sorted input before later sorting for output, making source YAML ordering part of the contract.
