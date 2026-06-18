## sources/test-tools/syzkaller/pkg/kcidb/client.go

Purpose: converts syzkaller dashboard bug reports into KCIDB JSON and submits them to a REST endpoint or file.

Important APIs/types/functions: `Client`, `NewClient`, `Close`, `RESTSubmit`, `Publish`, `PublishToFile`, global `Validate`, `kcidbValidate`, `convert`, `normalizeRepo`, and `extID`.

Control flow: `Publish` resolves target OS/arch, marshals `convert` output, optionally validates with `kcidb-validate`, then POSTs JSON with bearer token. Conversion always creates checkout/build records; build-error titles mark build `FAIL`, otherwise a failing syzkaller test record is emitted with output resources and misc dashboard fields.

State and persistence: `PublishToFile` writes JSON to a requested file. Client holds context/origin/REST URI/token but `RESTSubmit` currently uses a plain `http.Client` without binding request to context.

Dependencies and integration: integrates dashboard `dashapi.BugReport`, target metadata, external `kcidb-validate`, HTTP, JSON schema structs in `schema.go`, and KCIDB REST API.

Risks: build failure detection is string-based on title. `RESTSubmit` only accepts HTTP 200. Empty/missing token still produces an Authorization header. Validator absence logs to stderr and allows publish.

Test signals: no direct tests in this work item; correctness depends on JSON schema compatibility and dashboard integration.
