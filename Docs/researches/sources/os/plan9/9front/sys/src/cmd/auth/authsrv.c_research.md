# File Research: sources/os/plan9/9front/sys/src/cmd/auth/authsrv.c

Plan 9 authentication server protocol handler.

Key responsibilities:
- Reads `Ticketreq` messages and dispatches to Plan 9 ticket, challenge-response, password change, APOP/CRAM, CHAP, MSCHAP/MSCHAPv2, NTLM, VNC, and PAK handlers.
- Performs PAK key exchange and supports ticket-form mode that disables DES fallback.
- Looks up user/host/auth keys and secrets from auth databases, masking lookup failures with generated keys where needed.
- Issues client/server tickets and authenticators.
- Validates host `speaksfor` authorization via ndb.
- Implements password change protocol with old/new password validation and optional secret update.
- Implements Microsoft LM/NTLM/NTLMv2/MSCHAP hash and response checks.
- Maintains keyseed-backed deterministic fake DES keys for failed lookup masking.
- Logs success/failure through auth syslog.

Dependencies:
- Uses authsrv structures, libsec crypto, ndb, regexp/libc, and shared helpers from `authcmdlib.h`.

Research notes:
- Connection lifetime is capped by a 10-minute alarm.
- Some protocols exit after one successful exchange; others retry a bounded number of times.
- Security-sensitive comparisons use `tsmemcmp`.
