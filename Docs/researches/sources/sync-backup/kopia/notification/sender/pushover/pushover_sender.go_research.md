# sources/sync-backup/kopia/notification/sender/pushover/pushover_sender.go

Purpose: implements the registered `pushover` notification provider by POSTing JSON payloads to the Pushover API or a test override endpoint.

Important APIs/types/functions: `ProviderType`, `defaultPushoverURL`, `pushoverProvider`, `Send`, `Summary`, `Format`, and registry `init`. `Send` combines subject and body into Pushover's `message` field and adds `"html": "1"` for HTML format.

Control flow: construction validates options through `ApplyDefaultsAndValidate`. A send call builds a `map[string]string` with token, user, and message, selects either the default API URL or configured endpoint, marshals JSON, creates a context-aware POST request, sets `Content-Type: application/json`, sends via `http.DefaultClient`, and requires HTTP 200.

State and persistence behavior: no state is mutated after construction. Side effects are external HTTP requests; no retry or message persistence is performed.

Dependencies/integration points: plugs into `sender.GetSender`, depends on Pushover's HTTP API contract, and shares message format constants. Risks include using the default HTTP client without custom timeouts, accepting only status 200, not reading error body details, and no support for Pushover priorities/devices. Tests cover plain and HTML JSON payloads, endpoint override, HTTP status failure, connection failure, required options, and merge behavior.
