# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/wep.c

Implements a factotum `wep` protocol for configuring wireless WEP keys on a supplied Plan 9 ether device. All work occurs after finding a key and writing device control commands.

`wepinit` searches for a key with at least one private `!key1`, `!key2`, or `!key3`, then stores it in state. `wepwrite` accepts a device name, requires it to start with `#l`, dials its control channel, writes available keys, optional `essid`, and `crypt on`.

There is no meaningful read phase; `wepread` is a phase error. Key prompt is `!key1? !key2? !key3? essid?`.
