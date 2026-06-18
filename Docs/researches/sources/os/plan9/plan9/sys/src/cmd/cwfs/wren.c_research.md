# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/wren.c

Normal disk/file-backed block device backend.

Key responsibilities:
- `dataof()` maps a directory path to `<dir>/data`, otherwise duplicates the file path.
- `wreninit()` opens the underlying `/dev/sdXX/data` or mapped file, determines native block size via `inqsize()`, computes native sector count and cwfs block count.
- `wrensize()` returns logical cwfs block count.
- `wrenread()` reads one `RBUFSIZE` block via `pread`.
- `wrenwrite()` writes one `RBUFSIZE` block via `pwrite`.

Important interactions:
- `sdof()` builds `/dev/sd<ctrl><target>` paths for unmapped devices.
- Error counters `cons.nwrenre` and `cons.nwrenwe` are incremented on I/O failures.

Research notes:
- If geometry block size is absent or implausible, it falls back to 512-byte sectors.
- Logical block addressing uses byte offset `b * RBUFSIZE`, independent of native sector multiplier once size is computed.
