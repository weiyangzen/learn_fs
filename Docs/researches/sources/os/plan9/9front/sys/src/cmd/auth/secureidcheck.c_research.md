# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secureidcheck.c

RADIUS-based SecureID/token checker used by auth services including secstored. It constructs RADIUS Access-Request packets, sends them over UDP, verifies replies, and interprets accept/reject/challenge responses.

Important behavior:
- Defines RADIUS packet and attribute constants from RFC2138.
- `hide()` computes RADIUS User-Password hiding using MD5(shared secret + request authenticator), assuming pass length up to 16 chars.
- `authcmp()` verifies response authenticator.
- `rpc()` marshals a request, sends to a UDP destination, waits with 15-second alarms, retries once, verifies checksum, and unmarshals attributes.
- `secureidcheck()` rejects obviously invalid token strings, reads RADIUS shared secret from NDB, optionally maps Plan 9 user id to RADIUS id, adds NAS-IP-Address/User-Name/User-Password attributes, and tries each `lra-radius` IP from NDB.
- Return value is `nil` on success or a static error string on failure.

Interfaces/dependencies:
- Uses global `Ndb *db` supplied by caller.
- Opens local NDB for RADIUS server lookup.
- Logs to `auth`.

Risks/notes:
- Comment acknowledges UDP/RADIUS limitations: timeout selection, lost replies, and one-time token retry behavior.
- Request authenticator is seeded from `fastrand()`, appropriate for legacy Plan 9 context but weak by modern cryptographic standards.
