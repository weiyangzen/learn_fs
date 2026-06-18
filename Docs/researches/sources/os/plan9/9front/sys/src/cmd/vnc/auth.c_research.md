# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/auth.c

## Role

`auth.c` implements RFB/VNC version negotiation and authentication for both the VNC viewer and server programs.

## Client-Side Behavior

- `vnchandshake()` reads the server version banner, accepts RFB 3.3, 3.7, 3.8, Darwin 3.889, and 4.0 as compatible variants, then responds as RFB 3.8.
- `vncauth()` negotiates authentication according to the selected protocol version.
- For RFB 3.3 it reads a single authentication type; for newer versions it scans the offered list and selects the highest supported type up to VNC auth.
- Supports no-auth and classic VNC challenge-response.
- Uses Plan 9 factotum via `auth_respond()` and `auth_getkey` with `proto=vnc role=client`.

## Server-Side Behavior

- `vncsrvhandshake()` sends an RFB 3.3 banner and reads the client banner.
- `vncsrvauth()` creates a VNC challenge with `auth_challenge()`, writes the challenge, reads the response, validates it through factotum, and sends VNC auth status.

## Notable Limitations And Risk Areas

- Server-side negotiation is fixed to RFB 3.3 style.
- Client-side auth chooses only no-auth or VNC auth, ignoring stronger modern security types.
- TLS, when used by callers, is outside this file.
- Authentication errors are propagated with `werrstr()` or fatal server messages depending on side.
