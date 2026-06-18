# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/words/wrtape

Purpose: RC script to back up a range of Venti arenas to tape.

Key behavior:
- Computes arena range from tape number, rewinds tape device, fetches arena names from an HTTP index, locates their devices, logs backup progress, writes each arena with `venti/rdarena` piped through `scuzz`, writes file marks, then rewinds.

Dependencies:
- Uses `hoc`, `scuzz`, `hget`, `grep`, `sed`, `date`, `venti/rdarena`, and `/sys/log/ventibackup`.

Notable details:
- Hard-codes host `iolaire` and tape device `/dev/sd03`.
