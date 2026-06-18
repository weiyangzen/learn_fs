# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.3/rexec.c

## Purpose
Implements historical `rexec()`, connecting to a remote exec server and sending credentials/command.

## Behavior
Resolves the host, optionally fills username/password via `ruserpass()`, connects to the requested TCP port with exponential retry on refused connections, optionally opens a secondary listening socket for stderr, writes secondary port, username, password, and command as NUL-terminated strings, reads the server status byte, prints server error text to stderr on failure, and returns the connected socket on success.

## Dependencies
Depends on DNS (`gethostbyname()`), sockets, `ruserpass()`, `err/warn`, and classic rexec protocol behavior.

## Risks And Notes
This sends the password in cleartext, as noted in the source. The API is legacy and network-security-sensitive.
