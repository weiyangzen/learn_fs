# sources/object-store/openstack-swift/swift/cli/form_signature.py

Purpose: generates a FormPost middleware HMAC signature and sample HTML form for browser uploads.

Important APIs: `main(argv)` validates positional arguments, computes expiry, signs the five-line FormPost payload using HMAC-SHA1, prints the signature, and emits a sample multipart form.

Control flow: with incorrect argument count it prints syntax and sample usage. Otherwise it validates non-negative max file size, positive max file count, positive seconds, and a `/v1/account/container[/prefix]` path. It signs `path`, `redirect`, `max_file_size`, `max_file_count`, and `expires` joined by newlines using the supplied key encoded as UTF-8.

State and persistence: no persistence; output goes to stdout. The only time-dependent state is `expires = now + seconds`.

Dependencies and integration: matches Swift FormPost middleware signature semantics and account temp URL key usage.

Risks: prints sample HTML containing raw path and redirect values without escaping, so output should be treated as operator guidance rather than sanitized templating. SHA1 is protocol-defined here. Tests should cover argument validation, exact signing payload, byte/unicode key behavior, and generated form fields.
