# sources/object-store/openstack-swift/swift/cli/drive_audit.py

Purpose: scans kernel logs for device errors, maps kernel devices to mounted Swift device paths, optionally unmounts failed devices and comments `/etc/fstab`, then writes recon cache error counters.

Important APIs: `get_devices()`, `get_errors()`, `comment_fstab()`, and `main()`.

Control flow: `main()` reads `[drive-audit]` config, builds regexes from config or defaults, initializes logging, discovers mounted devices below `device_dir`, scans recent matching log files backwards until the time window or boot boundary, and counts matching kernel device errors. Devices exceeding `error_limit` are either logged or unmounted with `umount -fl` and removed from fstab. Recon cache is updated with per-mount errors and total `drive_audit_errors`; systemd daemon reload runs after fstab edits.

State and persistence: reads `/dev/block`, `/proc/mounts`, `/proc/partitions`, and log files. It may mutate mount state and `/etc/fstab`; it writes recon cache files under `recon_cache_path`.

Dependencies and integration: uses Swift `backward`, logging, `dump_recon_cache`, recon middleware consumption, and OS commands/files.

Risks: high operational blast radius if regexes match incorrectly or device mapping is wrong. `comment_fstab()` rewrites `/etc/fstab` via `/etc/fstab.new`. Time parsing depends on locale and log format, with special handling for year rollover and ISO timestamps.

Test signals: mock proc/dev/log inputs, year rollover, ISO timestamps, regex config, unmount disabled/enabled paths, fstab rewrite, recon cache writes, and no-device behavior.
