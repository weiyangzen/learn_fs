# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9fsys.c

Implements Fossil's named filesystem registry and a large console command surface for configuring, opening, inspecting, repairing, and controlling filesystems.

Key behavior:
- Maintains global `Fsys` list with name, device, Venti host, open `Fs`, Venti session, refcount, and policy flags.
- Provides `fsysGet()`, `fsysPut()`, `fsysGetRoot()`, permission policy accessors, and filesystem epoch lock wrappers used by 9P code.
- Parses and prints Fossil mode strings.
- CLI commands cover config/open/unconfig/venti/close, sync/halt/unhalt, snapshots, snapshot timing and cleanup, vac, df, remove, clri, create, stat, wstat, check, epoch, low-level block and label edits, block freeing, and clearing entries/pointers.
- `fsysOpen()` dials Venti unless disabled, computes cache size, opens the disk with `fsOpen()`, records noauth/noperm/wstat/noatime flags, and reloads users for main.
- `fsysCheck()` wires `Fsck` callbacks for optional repair operations and halts/unhalts around checking.
- `fsysInit()` installs formatters and registers CLI commands.

Important implementation details:
- `ventihost()`, `myDial()`, and `myRedial()` centralize Venti address handling and logging.
- `fsysXXX()` dispatches commands either to a named filesystem, `all`, or the current console filesystem.
- Low-level commands operate under `fs->elk` and use cache/block label primitives directly.
- `freemem()` can size cache based on Plan 9 `#c/swap` when `mempcnt` is configured.

Risks and invariants:
- `fsysClose()` is explicitly disabled and tells operators to halt and kill Fossil instead.
- Several commands can directly mutate on-disk labels/blocks, so they are operator repair tools, not safe user APIs.
- `fsysConfig()` appears to look up an existing filesystem using `part` rather than `name`, which is worth checking before modification.
