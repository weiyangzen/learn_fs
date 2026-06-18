# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secureidcheck.c

Implements SecurID validation through RADIUS (RFC 2138). It builds Access-Request packets, hides the user password/token with MD5(shared secret + authenticator), sends UDP requests to configured `lra-radius` hosts, validates response authenticators, and interprets accept/reject/challenge codes.

Configuration comes from ndb: RADIUS shared secret, optional uid-to-rid mapping, and radius server IPs. It adds NAS-IP-Address based on local IPv4 interface and logs outcomes to `auth`.

Limitations are documented in the file header: UDP loss and one-use token semantics make retry and timeout choices inherently flawed.
