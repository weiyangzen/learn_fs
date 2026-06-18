<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/api/client.go -->
# sources/test-tools/syzkaller/dashboard/api/client.go research

Purpose: Go client helper for reading syzkaller dashboard JSON API endpoints and text artifacts.

Important APIs, types, and functions: `Client` stores base URL, OAuth token, throttling flag, request constructor/doer hooks, and requested access level. `NewClient`, `NewTestClient`, `SetAccess`, `BugGroups`, `Bug`, `Text`, `query`, and `queryURL` implement API operations. `BugGroupType` bitmasks select open/fixed/invalid groups, and a global ticker throttles unauthenticated public requests.

Control flow: higher-level methods build endpoint paths, call `query`, which calls `Text`, reads the body, checks HTTP status, unmarshals JSON, and reflects on the `Version` field. `Text` adds a bearer token when present or waits on the one-second throttler when not. `queryURL` unescapes HTML links, appends `json=1` and `access`, and resolves against the configured dashboard URL.

State and persistence: client state is in-memory only. The package-level ticker is shared across tokenless clients.

Dependencies and integration: depends on `net/http`, JSON, URL parsing, reflection, and the DTOs from `api.go`. It integrates with dashboard access-level query parameters and OAuth bearer-token support.

Risks: reflection assumes result is a pointer to a struct with integer `Version`; misuse panics. Tokenless calls are globally throttled and can serialize unrelated clients. Error messages include up to 1024 bytes of response body, which is useful but may expose server text in logs.

Test signals: injected constructor/doer via `NewTestClient`, URL query construction, token header behavior, throttling path, HTTP error handling, JSON unmarshal failures, and unsupported version errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/api/client.go -->
