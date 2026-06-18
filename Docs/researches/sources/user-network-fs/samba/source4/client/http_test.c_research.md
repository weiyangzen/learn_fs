# sources/user-network-fs/samba/source4/client/http_test.c

## Purpose
Provides a small Samba HTTP client test utility. It connects to an HTTP or HTTPS endpoint, optionally uses Basic auth from Samba credentials, sends a POST request to a configurable URI, reads a bounded response, and prints the response body.

## Important APIs, types, and functions
- `struct http_client_info` stores connection, port/address, TLS params, credentials, loadparm context, and URI.
- `send_http_request()` builds an `HTTP_REQ_POST`, adds `User-Agent` and `Accept` headers, calls `http_send_auth_request_send()` with `HTTP_AUTH_BASIC`, then reads the response with `http_read_response_send()`.
- `main()` parses `--usetls`, `--ip-address`, `--port`, `--cacart`, `--uri`, and `--rsize` plus common Samba and credential options.

## Control flow
The program initializes talloc and Samba command-line config, sets defaults (`localhost`, `/_search?pretty`, port `8080`, response size about 8 MiB), configures credentials, creates a tevent context, then retries the connection up to four times. With TLS enabled, it creates client TLS parameters from the CA certificate before `http_connect_send()`. After a successful connection, it sends one request and returns success only for HTTP status 200 with a non-empty body.

## State and persistence behavior
The utility is stateless beyond its process memory and network connection. It may allocate a copy of non-anonymous credentials. It prints response bodies to stdout and debug/errors through Samba logging macros. No files are written except any implicit TLS/config access from Samba libraries.

## Dependencies and integration points
Uses Samba HTTP client APIs, tevent polling helpers, TLS helper APIs, command-line credentials, and loadparm. It is likely intended for blackbox or manual testing of Samba services exposing HTTP endpoints.

## Risks and edge cases
- The option is named `--cacart` in code and help text, likely a typo for `--cacert`; scripts must use the implemented spelling.
- TLS requires a CA file and does not use system CAs in this code path.
- Connection polling lacks an explicit timeout around `http_connect_send()`, while request and response operations use 10-second endtimes.
- It hardcodes POST with an empty body, so it is not a general HTTP client.
- It treats non-200 and zero-length responses as failures after printing diagnostic text.

## Test signals
No direct test script is in this subset. Useful tests would cover anonymous and credentialed Basic auth, TLS CA validation, retry behavior on initial connection failure, response-size limits, non-200 status handling, and the `--uri`/`--rsize` options.
