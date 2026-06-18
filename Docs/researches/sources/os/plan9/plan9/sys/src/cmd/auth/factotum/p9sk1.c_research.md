# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/p9sk1.c

Implements Plan 9 shared-secret authentication protocols `p9sk1` and the incomplete `p9sk2`. It manages ticket requests, tickets, authenticators, challenges, and authinfo secrets.

Client `p9sk1` starts by generating and reading a client challenge; server waits for that challenge, sends a ticket request, receives ticket/authenticator, and returns a server authenticator. `p9sk2` skips the initial challenge and is marked flawed/incomplete.

Client key lookup supports both normal `role=client` keys and `role=speakfor` keys, allowing the host owner to speak for another local user while preserving restrictions for non-owner callers. Tickets are fetched from an auth server or locally generated when possible. Key addition accepts `!hex` or `!password`, converting to DES key material.
