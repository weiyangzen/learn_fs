# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/auth.c

RFB 3.3 handshake and VNC challenge-response authentication.

Key responsibilities:
- Sends or receives the fixed `RFB 003.003\n` version string for client/server roles.
- Implements VNC DES challenge encryption, including VNC’s bit-reversed DES key bytes.
- Uses Plan 9 auth/factotum for client responses and server-side challenge validation.
- Falls back to an interactive `/dev/cons` password prompt for clients without suitable factotum keys.
- Sends server-side VNC auth challenge and final OK/failure response.

Important behavior:
- Client auth supports no-auth, failure-with-reason, and VNC auth.
- Client key lookup uses `proto=vnc role=client server=...`.
- Server challenge uses `proto=vnc role=server user=...`.

Risks:
- Protocol is old RFB 3.3 VNC auth, not modern secure authentication.
- Password fallback reads raw console input and zeroes only the local password buffer afterward.
