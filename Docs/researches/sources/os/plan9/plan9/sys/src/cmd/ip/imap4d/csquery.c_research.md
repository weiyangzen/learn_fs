# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/csquery.c

Connection-server lookup helper. It writes a query such as `!attr=value` to `/net/cs`, scans returned NDB-style records for the requested attribute, and returns a duplicated value string when found.
