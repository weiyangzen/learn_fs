# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/authp9any.c

Implements 4th Edition `p9any` / `p9sk1` authentication for u9fs, based on older Plan 9 auth code.

Major pieces:
- Defines ticket, ticket request, and authenticator wire structures.
- Provides local DES encrypt/decrypt wrappers and password-to-key conversion.
- Conversion helpers serialize/deserialize ticket requests, tickets, and authenticators.
- `p9anyinit` reads a key file, defaulting to `/etc/u9fs.key`, expecting three lines: password, auth id, auth domain.
- `AuthSession` tracks per-auth-fid state: protocol negotiation, challenge, ticket request, ticket, and final establishment.
- `p9anyauth`, `p9anyread`, `p9anywrite`, `p9anyattach`, and `p9anyclunk` implement the 9P auth fid lifecycle.
- Exports `Auth authp9any`.

State flow:
- Server advertises `p9sk1@authdom`.
- Client selects `p9sk1 authdom`.
- Client sends challenge.
- Server sends encrypted ticket request.
- Client sends ticket plus authenticator.
- Server verifies ticket, challenge, and authenticator, then returns server authenticator and marks session established.
- Attach succeeds only when uname/aname match the established auth session.

Notable behavior:
- Uses DES-era p9sk1 auth.
- Clears some secret/session memory on clunk.
- Depends on external `block_cipher`, `key_setup`, `randombytes`, fid helpers, and u9fs global `autharg`.
