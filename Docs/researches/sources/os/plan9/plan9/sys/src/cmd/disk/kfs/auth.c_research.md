# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/auth.c

This file implements old 9P1 challenge/response authentication and shared auth policy flags.

Key behavior:
- Defines `allownone`, `nvr`, and `didread`.
- `mkchallenge` lazily reads NVRAM auth data, seeds randomness, fills `Chan.chal`, and resets authenticator replay state.
- `authorize` validates old 9P1 tickets and authenticators using authsrv conversion helpers.
- Allows local console service channels and boot-time `wstatallow`.
- Handles `none` attach policy using `allownone` or prior channel authentication.
- Checks ticket type, authenticator type, challenge match, replay id bitmap, and ticket names.
- On success, rewrites `in->uname` to the server uid and creates the response authenticator in `ou->rauth`.

Dependencies:
- `Chan` challenge/replay fields from `dat.h`.
- `Oldfcall` from `9p1.h`.
- `Nvrsafe`, `Ticket`, `Authenticator`, and conversion routines from auth headers.

Notable detail:
- `Nvrsafe nvr;` appears twice in the file text; in this old Plan 9 build context that may have compiled historically, but in modern C this duplicate definition would be suspect.
