# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/main.c

Bootstraps drawterm's hosted Plan 9 environment. It sets `eve`, verifies critical C type sizes with `sizebug`, initializes OS/proc/print/screen subsystems, resets and initializes channel devices, installs quote formatting, binds core devices into `/dev`, `/net`, and `/`, opens `/dev/cons` as fd 0/1/2, then calls `cpumain`.

Also provides credential helpers:
- `getkey` prompts for `<user>@<dom> password` using `readcons`.
- `findkey` scans `secstorebuf` for `key proto=p9sk1 dom=<dom> user=... !password=...` entries and returns the matching user/password.

Notable behavior:
- Assumes 32-bit `long`/`ulong`, which is explicitly asserted as a drawterm portability requirement.
- `findkey` skips overlong secstore lines and clears its stack buffer before returning a copied password.
