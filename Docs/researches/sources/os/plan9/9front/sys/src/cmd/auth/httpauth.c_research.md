# File Research: sources/os/plan9/9front/sys/src/cmd/auth/httpauth.c

Command-line HTTP Basic authentication checker.

Key responsibilities:
- Accepts either `user pass` or a Basic Authorization value.
- Strips optional `Basic ` prefix and base64-decodes credentials.
- Splits decoded `user:password`.
- Rejects empty usernames and bad base64/format.
- Calls `auth_userpasswd` and prints the authenticated username on success.

Dependencies:
- Uses Plan 9 auth library and base64 decode helper.
