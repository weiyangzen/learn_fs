# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/p9cr.c

Factotum protocol module for legacy Plan 9 textual challenge/response and VNC DES challenge auth.

Key responsibilities:
- Implements `p9cr` client/server challenge-response flow.
- Implements `vnc` client challenge-response using bit-reversed DES key bytes.
- Client mode reads a challenge and returns the computed response.
- Server mode obtains a challenge from authsrv, receives a response, and validates it through authsrv.
- Produces `AuthInfo` after successful server-side validation.
- Provides VNC key parsing from `!password`.

Dependencies:
- Uses factotum key lookup, Plan 9 authsrv challenge requests, DES routines, and ticket/authenticator conversion.

Notable risks:
- The `p9cr` client path maps to `p9sk1` key material for the DES response.
- VNC password handling truncates/zero-pads to 8 DES-key bytes.
