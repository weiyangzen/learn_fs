# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/iobuf.c

I/O buffer cache implementation for cwfs. It hashes `(Device*, address)` into `Hiob` lists, returns locked mapped buffers, flushes dirty buffers, and validates block tags.

Important behavior:
- `getbuf()` searches active hash chains, promotes hits, evicts oldest unlocked non-reserved buffers, writes dirty victims, and optionally reads from device.
- `Bprobe` returns nil on cache miss without loading.
- Reserved buffers (`Bres`) are not evicted to avoid recursion/deadlock with pseudo devices.
- `syncblock()` writes at most one dirty buffer per hash line per pass; `sync()` repeats until clean or bounded attempts expire.
- `putbuf()` immediately writes `Bimm` buffers, unmaps, and unlocks.
- `checktag()` validates trailer tag/path and prints detailed diagnostics; `settag()` updates tag/path and marks modified.
