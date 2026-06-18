# File Research: sources/os/plan9/plan9/sys/src/cmd/plumb/fsys.c

Synthetic 9P filesystem for the Plan 9 plumber service.

Key responsibilities:
- Publishes and mounts `/mnt/plumb` through `/srv/plumb.$user.$pid`.
- Exposes `rules`, `send`, and per-port files.
- Handles 9P version, attach, walk, open, read, write, clunk, stat, and flush operations.
- Queues plumb messages for all fids open on a destination port.
- Holds messages for ports whose client is being started.
- Parses writes to `send`, matches rules, starts clients, or delivers to ports.
- Supports live rules updates through writes to the `rules` file.

Important behavior:
- `addport()` dynamically appends readable port files and records them in `ports`.
- `queuesend()` snapshots currently open fids so each reader gets the message once.
- `drainqueue()` pairs queued read requests with queued send requests and handles partial reads using per-fid offsets.
- Opening a port queues any held startup messages.
- Opening `rules` for write is serialized by `rulesref`.
- Truncating `rules` clears current rules before accepting new rule text.

Dependencies:
- Uses Plan 9 threads, 9P `Fcall`, `plumbpack/unpack`, `/dev/time`, `/srv`, and global rule/matching functions.

Notable risks:
- Global queue state is complex and depends on `queue` locking discipline.
- Per-message delivery to every open fid can retain queued messages until all recipients read or close.
- Rules write finalization on clunk can lose parse errors for incomplete final rules.
- `NDIR` caps total ports at 50.
