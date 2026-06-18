# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/config.c

Configuration parser, config-block merger, system initializer, and device-copy helper for cwfs. It parses compact device expressions and the persistent config block.

Important behavior:
- Device syntax covers concatenation, interleave, mirrors, fake worm, none, mapped file, wren/worm/labeled worm, ro companion, jukebox, cache-worm, partitions, and byte-swapped devices.
- Supports numeric iteration syntax with `<start-end>`.
- `mergeconf()` reads config block keywords: `service`, auth/noatime/readonly switches, `newcache`, `filsys`, and declared geometry parameters.
- `sysinit()` reads/creates config, fills missing geometry declarations, rewrites modified configs, compiles file system device expressions, reams/recovers/init devices, and optionally copies devices/worms.
- `arginit()` provides interactive boot-time config commands including `config`, `nvram`, `filsys`, `ream`, `recover`, `copyworm`, `copydev`, and policy toggles.
- Copy helpers stream block-by-block and include basic sizing/sanity checks.
