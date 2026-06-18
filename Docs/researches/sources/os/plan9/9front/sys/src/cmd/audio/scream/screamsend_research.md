# File Research: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamsend

Rc wrapper for sending local audio as Scream multicast.

Key behavior:
- Accepts optional IPv4 interface addresses.
- Defaults interfaces from `/net/ipselftab`.
- Dials UDP multicast `239.255.77.77!4010` with multicast add options.
- Sends `/dev/audio` through `audio/screamenc`.

Dependencies:
- Uses Plan 9 `rc`, `aux/dial`, multicast network control, and `audio/screamenc`.

Research notes:
- Non-address arguments trigger usage.
