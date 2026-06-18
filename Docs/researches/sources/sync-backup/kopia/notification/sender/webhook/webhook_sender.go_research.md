# sources/sync-backup/kopia/notification/sender/webhook/webhook_sender.go

Purpose: implements the registered generic HTTP webhook notification provider.

Important APIs/types/functions: `ProviderType`, `webhookProvider`, `Send`, `Summary`, `Format`, and registry `init`. It sends the message body as the request body, subject as a header, option headers from newline-separated `key: value` lines, and message headers as overrides/additions.

Control flow: construction validates endpoint/method/format. `Send` creates a context-aware request using configured method and endpoint, sets `Subject`, parses configured headers line by line, copies message headers, sends with `http.DefaultClient`, closes the response body, and treats any status other than 200 as an error.

State and persistence behavior: stateless after option capture. Side effects are external HTTP requests only; there is no retry, queueing, or durable delivery state.

Dependencies/integration points: integrates with the sender registry and generic HTTP receivers. Risks include no custom timeout/client, no content type default except what the caller supplies, accepting invalid HTTP methods until send time, ignoring malformed configured header lines, and requiring exactly 200 rather than all 2xx. Tests cover headers, methods, formats, status/connection failures, invalid URL/scheme, invalid method at send time, summary, and merge behavior.
