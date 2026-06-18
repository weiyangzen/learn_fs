# sources/test-tools/kdevops/terraform-provider-rcloud/internal/provider/client.go

## Purpose
This Go file implements the minimal HTTP client used by the custom `rcloud` Terraform provider. It models VM create/read/delete/start/stop operations against an rcloud REST API under `/api/v1/vms`.

## Important APIs, Types, And Functions
`APIClient` carries endpoint, bearer token, default SSH user/public-key file metadata, and an optional `*http.Client` injection point for tests. `VM` models API read responses with ID, name, state, vCPU count, memory in MB, and optional IP address. `CreateVMRequest` is the JSON payload for VM creation, including optional SSH user and public key contents. `CreateVMResponse` carries the create response ID/name/state. `newHTTPClient()` returns the injected client or a 30-second timeout client. `CreateVM()`, `GetVM()`, `DeleteVM()`, `StartVM()`, and `StopVM()` construct HTTP requests, attach JSON or authorization headers, check expected status codes, and decode or discard response bodies.

## Control Flow
Each client method builds a URL by concatenating `Endpoint` with a fixed API path. Create marshals the request body, posts JSON, requires HTTP 201, and decodes the creation response. Read performs GET, maps 404 to a generic "VM not found" error, requires 200, and decodes `VM`. Delete, start, and stop call DELETE or POST action endpoints and require HTTP 200.

## State And Persistence
The client itself is stateless besides configuration fields. State lives in the remote rcloud API. The code persists no local files, but operations mutate remote VM lifecycle state. Request timeouts are per-operation through the HTTP client.

## Dependencies And Integration Points
It depends only on Go standard library packages `bytes`, `encoding/json`, `fmt`, `io`, `net/http`, and `time`. It is consumed by `provider.go` for Terraform provider configuration and by `resource_vm.go` for resource CRUD. The REST API contract is implicit: status codes, JSON field names, and action routes must match the rcloud service.

## Risks And Test Signals
URL concatenation does not normalize trailing slashes, so `Endpoint` values ending in `/` can produce double slashes. Not-found is a plain error string, which the resource currently treats as a diagnostic instead of removing Terraform state. Delete expects only 200 and may reject common 204 delete responses. Error bodies are surfaced verbatim and may include sensitive server output. Unit tests can inject `HTTPClient` with a fake transport or `httptest.Server` to cover headers, JSON payloads, expected status handling, timeout use, and malformed JSON responses.
