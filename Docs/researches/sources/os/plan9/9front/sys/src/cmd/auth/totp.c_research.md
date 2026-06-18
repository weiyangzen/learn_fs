# File Research: sources/os/plan9/9front/sys/src/cmd/auth/totp.c

Small factotum client for generating/reading TOTP values.

Important behavior:
- Usage accepts `fmt`; optional `-k keypat` overrides the default key pattern.
- Builds factotum query params as `proto=totp label=<arg>` or `proto=totp <keypat>`.
- Opens `/mnt/factotum/rpc`, starts an auth RPC, issues `start`, then `read`, and prints the returned argument.

Interfaces/dependencies:
- Uses `auth_allocrpc`, `auth_rpc`, and `/mnt/factotum/rpc`.
- Installs quote formatting to safely include labels.
