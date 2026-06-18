# sources/sync-backup/kopia/notification/sender/webhook/webhook_sender_options.go

Purpose: defines webhook configuration validation and merge behavior.

Important APIs/types/functions: `Options` contains endpoint, HTTP method, format, and newline-separated headers. `ApplyDefaultsAndValidate` defaults method and format, validates endpoint URL and scheme, and `MergeOptions` overlays fields using create/update semantics.

Control flow: validation sets `POST` when method is empty, calls shared format validation with default `txt`, parses endpoint with `url.ParseRequestURI`, rejects non-HTTP(S) schemes, then redundantly checks for empty format. Merge copies endpoint, method, headers, and format, then validates the result.

State and persistence behavior: this struct is the persistent JSON profile shape for webhook sender configuration. Headers are stored as a raw text blob rather than structured key/value JSON.

Dependencies/integration points: consumed by sender registration and profile update code. Risks include method syntax not being validated until `http.NewRequestWithContext`, inability to clear a field in update mode with zero values, and unstructured headers allowing malformed lines to be silently ignored by the sender. Tests cover defaults through construction, URL/scheme validation, invalid method at send time, and merge updates.
