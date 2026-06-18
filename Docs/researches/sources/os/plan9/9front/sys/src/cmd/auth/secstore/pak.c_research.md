# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/pak.c

Secstore Password Authenticated Key Exchange implementation.

Key responsibilities:
- Defines fixed PAK group parameters and initializes them lazily.
- Computes long password hash `H` and inverse `Hi` from version, client id, and passphrase hash.
- Provides `PAK_Hi` for account password verifier generation.
- Implements short hashes for server proof, client proof, and session secret derivation.
- Implements `PAKclient`: sends client id and blinded exponent, verifies server proof, sends client proof, and installs session secret.
- Implements `PAKserver`: parses first client message, loads password verifier, sends server proof, verifies client proof, installs session secret, and updates failed login counters.

Dependencies:
- Uses libmp modular arithmetic, SHA1/HMAC-SHA1, secstore `SConn`, password database helpers from `password.c`, and `secstore.h`.

Notable risks:
- File comments note PAK patent/licensing history.
- Authentication failure updates account failed counters and may trigger lockout behavior in password handling.
