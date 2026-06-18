# File Research: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamrecv

Rc wrapper for receiving Scream multicast audio.

Key behavior:
- Accepts optional IPv4 interface addresses.
- Defaults interfaces by reading IPv4 unicast entries from `/net/ipselftab`.
- Runs `aux/listen1` on UDP multicast `239.255.77.77!4010` with multicast add options.
- Pipes received data through `audio/screamdec` to `/dev/audio`.

Dependencies:
- Uses Plan 9 `rc`, `aux/listen1`, multicast network control, and `audio/screamdec`.

Research notes:
- Non-address arguments trigger usage.
