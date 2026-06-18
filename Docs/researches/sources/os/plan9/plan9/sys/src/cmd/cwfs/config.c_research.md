# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/config.c

Configuration parser and boot-time system initialization for cwfs. It parses compact device expressions, reads/writes the on-disk configuration block, supports interactive configuration commands, and provides copy/recovery utilities.

Key responsibilities:
- Parses device expressions through `iconfig()`, `config()`, `config1()`, and `cnumb()`.
- Device grammar supports:
  - `w`, `r`, `l` for wren, worm, labelled worm devices.
  - `c` for cache/worm devices.
  - `j` for jukebox devices.
  - `f` for fake WORM wrappers.
  - `o` for read-only side of last cw.
  - `p` for percentage partitions.
  - `x` for byte-swapping device wrappers.
  - `(...)`, `[...]`, `{...}` for concatenation, interleave, and mirror groups.
  - `<n-m>` numeric iterators.
- `devcmpr()` compares device trees structurally for mapping and identity checks.
- `map()` applies optional wren-to-file or wren-to-device mappings from `devmap`.
- `mergeconf()` parses the on-disk config text block, merging service name, filsys declarations, and filesystem parameter declarations.
- `cmd_printconf()` prints NVRAM config and active config block, suppressing obsolete `ip*` commands.
- `sysinit()` reads config, writes missing config parameters, compiles each `Filsys` device tree, initializes/reams/recovers devices, then optionally runs copy operations.
- `arginit()` implements interactive boot-time commands such as `config`, `nvram`, `filsys`, `ream`, `recover`, `service`, `copyworm`, `copydev`, `noauth`, `readonly`, and `resetparams`.

Copy/recovery utilities:
- `wormof()` handles fake-WORM special cases.
- `writtensize()` probes for last readable WORM block.
- `dowormcopy()` copies written WORM blocks from `main` to optional `output`.
- `dodevcopy()` copies one arbitrary configured device to another, bounded by smaller size.

Important interactions:
- Uses `nvrgetconfig()`/`nvrsetconfig()` for persistent config string storage.
- Reads/writes block 0 of `confdev` as `Tconfig`.
- Uses `Fspar fspar[]` to track compiled-in disk-layout parameters: `blocksize`, `daddrbits`, `indirblks`, `dirblks`, `namelen`.
- Calls `devream`, `devrecover`, `devinit`, `getbuf`, `settag`, `checktag`, and `querychanger`.

Research notes:
- This file preserves obsolete network config keywords to keep old config blocks parseable.
- If config parameters are absent, `sysinit()` writes defaults back into the config block and restarts config reading.
- `userabort()` is currently a stub returning 0, so long copy operations are not actually interruptible through that hook.
- The parser stores newly allocated `Device` nodes on `f.devlist`, but this list is used as an ownership/debug chain rather than a deallocation path.
