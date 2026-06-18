# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/mworm.c

Composite block-device implementations: concatenation, interleaving, partitions, and mirroring.

Key responsibilities:
- `mcat*` implements concatenated devices:
  - initializes children and stores child list.
  - size is sum of child sizes.
  - read/write selects child by cumulative range.
- `mlev*` implements interleaved/striped devices:
  - size is `n * min(child_size)`.
  - read/write dispatches by `b % n` and `b / n`.
- `part*` implements percentage-based partitions:
  - base and size are percentages of parent size.
  - size 0 means remainder/all 100%.
- `mirr*` implements mirrors:
  - size is minimum child size.
  - reads try children until one succeeds.
  - writes recursively write later mirrors first, then earlier/main device.

Important interactions:
- Uses generic `devinit`, `devsize`, `devread`, `devwrite` recursion.
- `Device.cat` union is shared by mcat, mlev, and mirror.

Research notes:
- Mirror write ordering is deliberate: mirrors are written before the main device so a power loss with main updated implies mirrors should already be updated.
- `mirrread()` reports failure only if every mirror read fails.
