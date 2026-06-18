# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_respond.c

This file performs a one-shot challenge response through factotum.

Key behavior:
- `auth_respond` opens `/mnt/factotum/rpc`, starts an auth RPC, writes challenge bytes, reads response bytes, and returns response length.
- Internal `dorpc` handles RPC verb dispatch and key callback requests.

Important details:
- Copies returned user text into the caller's buffer when available.
- Enforces caller-provided response buffer length.
