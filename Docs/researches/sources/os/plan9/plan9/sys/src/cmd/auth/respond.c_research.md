# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/respond.c

Small wrapper around `auth_respond`. It accepts auth params and a challenge, uses `auth_getkey` to obtain key material, writes the generated response to stdout, and appends a newline.

Useful for testing or scripting Plan 9 auth challenge responses.
