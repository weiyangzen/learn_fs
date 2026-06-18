# File Research: sources/os/plan9/9front/sys/src/cmd/auth/acmed.c

ACME v2 client for obtaining TLS certificates on Plan 9.

Key responsibilities:
- Discovers ACME directory endpoints from the provider URL, defaulting to Let's Encrypt production.
- Encodes base64url values and JSON strings for JWS requests.
- Signs RS256 JWS payloads through factotum using an RSA account key.
- Creates/uses an ACME account and submits new certificate orders from CSR subject names.
- Handles HTTP-01, DNS-01, or external command challenge fulfillment.
- Polls authorization and order status until valid, submits CSR, fetches certificate PEM, and writes it to stdout.
- Loads JWK public account key JSON, computes the ACME JWK thumbprint, and supports IDN conversion.

Dependencies:
- Uses Plan 9 `webfs` under `/mnt/web`, `factotum` `/mnt/factotum/rpc`, JSON library, libsec X.509/RSA helpers, and authsrv interfaces.

Research notes:
- Challenge command mode executes a user-supplied command with challenge type, domain, token, and authorization string.
- DNS challenge mode writes an ndb-style challenge file and refreshes `/net/dns`.
- Request signing depends on a matching factotum key spec.
