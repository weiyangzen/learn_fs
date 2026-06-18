# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/passwd.c

Client for changing Plan 9 and Inferno/POP passwords via the auth server. It requests an `AuthPass` ticket, asks for the old password, verifies it can decrypt the ticket, then loops prompting for optional new Plan 9 password and optional secret.

It marshals `Passwordreq` encrypted with the ticket key and sends it to the auth server until accepted. `asrdresp` handles `AuthOK` and `AuthErr` response framing.
