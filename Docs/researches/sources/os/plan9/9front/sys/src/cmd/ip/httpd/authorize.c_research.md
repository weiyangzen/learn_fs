# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/authorize.c

Basic-auth authorization helper for HTTPD. For a requested file path, it looks for a sibling `.httplogin`, tokenizes it as realm plus username/password pairs, and compares against parsed request credentials.

On missing `.httplogin`, access is allowed. On failed auth, it emits a `401 Unauthorized` response with `WWW-Authenticate: Basic realm="<realm>"`, content length, connection policy, optional body for non-HEAD requests, and log entry.

The comment notes the supplied auth username is used directly here, despite older intent text about realm user behavior.
