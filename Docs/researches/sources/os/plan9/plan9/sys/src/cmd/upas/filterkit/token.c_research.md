# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/token.c

- Role: Creates or checks short HMAC-based mail tokens.
- Key functions: `mktoken` masks the time-of-day in `ctime`, computes HMAC-SHA1 with the key, base64 encodes, and returns first 5 chars; `check_token` accepts tokens from the previous 14 days; `create_token` prints today’s token.
- Integration: Uses Plan 9 libsec SHA1/HMAC/base64 and String.
- Risks/notes: 5 base64 chars is a short token; security relies on deployment context and key secrecy.
