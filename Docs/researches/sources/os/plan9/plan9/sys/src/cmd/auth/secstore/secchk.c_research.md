# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secchk.c

Small diagnostic wrapper for `secureidcheck`. It opens auth/local ndb databases, prints current `user`, checks the provided PIN+SecurID response, and prints the returned result.

Used to test RADIUS/SecurID integration from the secstore context.
