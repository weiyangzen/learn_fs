# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/okpasswd.c

Checks password quality for auth tools. It trims trailing spaces, requires at least 8 characters, and rejects a small list of trivial passwords and their reverses.

Returns `nil` for acceptable passwords or an explanatory string for rejection.
