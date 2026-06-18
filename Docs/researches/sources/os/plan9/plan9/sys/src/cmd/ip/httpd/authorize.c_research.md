# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/authorize.c

Basic-auth gate for protected httpd directories. It searches the requested path’s directory for `.httplogin`, tokenizes the file as realm plus username/password pairs, and compares those against parsed request credentials.

If authentication is missing or invalid, it emits a `401 Unauthorized` response with `WWW-Authenticate: Basic`, content length, connection handling, and access-log entry. If no `.httplogin` exists, access is allowed.
