# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/pak.c

Implements secstore’s PAK password-authenticated key exchange. It defines fixed group parameters, derives `H(passphrase)` and inverse `Hi`, and uses SHA1-based confirmation hashes for server, client, and session keys.

`PAKclient` sends client identity and `m=g^x H`, verifies server `mu` and `k`, sends `k'`, and installs the session secret into `SConn`. `PAKserver` parses the first message, loads the user `PW`, computes `mu=g^y`, verifies client proof, updates failure counters, and installs the server-side session secret.

The code supports a zero-knowledge existence probe: if client `m` is zero, server reports account existence without authenticating.
