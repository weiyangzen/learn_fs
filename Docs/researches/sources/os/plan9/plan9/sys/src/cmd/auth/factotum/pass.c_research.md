# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/pass.c

Implements a simple password repository protocol named `pass`. It has no server-side exchange and only supports reading a stored user/password pair.

`passinit` finds a matching key, copies its public attributes into the current state, and enters `HavePass`. `passread` returns quoted `user password` from public `user` and private `!password`. `passwrite` is always a phase error.

Used by callers that need factotum-managed retrieval of username/password credentials. Key prompt is `user? !password?`.
