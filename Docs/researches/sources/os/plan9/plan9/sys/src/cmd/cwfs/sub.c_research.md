# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/sub.c

Large utility and dispatch module for cwfs. It contains filesystem lookup helpers, fid/path management, permissions, freelist allocation, formatting, queue/message buffers, generic device dispatch, reaming/recovery, and byte swapping.

Key responsibilities:
- Filesystem/channel/fid helpers:
  - `fsstr()`, `dev2fs()`, `fs_chaninit()`, `fileinit()`, `filep()`, `newfp()`, `freefp()`.
- Permissions and locks:
  - `iaccess()` implements owner/group/other/superuser checks.
  - `tlocked()` allocates/checks timed file locks.
  - `newwp()` and `freewp()` manage `Wpath` reference chains.
- Allocation/free:
  - `qidpathgen()` increments superblock qid generator.
  - `buffree()` recursively frees direct/indirect blocks and updates freelist, respecting cw written-block rules.
  - `bufalloc()` pops from free list, grows cw if full, clears/tag-initializes allocated blocks.
  - `addfree()` pushes blocks to freelist, spilling to `Tfree` blocks as needed.
- Formatting:
  - `%Z` formats device trees.
  - `%G` formats block tags.
  - `formatinit()` installs formatters.
- Filesystem initialization:
  - `rootream()` writes root directory block.
  - `superream()` writes superblock and free list.
- Message buffers and queues:
  - `mbinit()`, `mballoc()`, `mbfree()`.
  - `fs_recv()`, `fs_send()`, `newqueue()`.
- Generic device operations:
  - `devread()`, `devwrite()`, `devsize()`, `sdof()`, `superaddr()`, `getraddr()`, `devream()`, `devrecover()`, `devinit()`.
- Byte swapping:
  - `swab2()`, `swab4()`, `swab8()`, and `swab()` for tagged block types.

Important interactions:
- Central dispatch point for all `Device.type` implementations.
- `devwrite()` honors global `readonly` by returning success without writing, mainly for experiments.
- `swab()` knows every on-disk structure and tag type that needs endian conversion.

Research notes:
- `tlocked()` appears to have a suspicious condition: `if(t1 != nil && t->time == 0) t1 = t;` means it never records a free lock while `t1` is nil. Existing behavior may intentionally simulate lock exhaustion, but the code comment suggests free-lock reclamation is expected.
- `mbfree()` sets `mb->magic = 0` after checking it; `mballoc()` restores `Mbmagic`.
- `fs_send()` waits briefly for a reader (`waitedfor`) and aborts if none appears, treating send-before-reader as a bug.
- `devream()` recursively reams child devices, then writes root/super for top-level non-cw devices or calls `cwream()` for cw.
