# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup

Purpose: main test VM setup orchestrator after kernel selection. It configures result storage, scratch disks, optional Filestore/NFS, PTS, syslog capture, metadata, and appliance state before tests run.

Important flow: source GCE funcs, test config, runtime utils, and `/run/test-env`; protect rsyslog/sshd from OOM; fetch config from GCS if missing; derive Filestore parameters from `NFSSRV`; if reboot setup marker exists, append dmesg and remount Filestore/PTS only. First boot runs pre-setup hooks, logs disk setup, decodes original command line to `/var/www/cmdline`, computes partition sizes unless PTS or blktests mode, applies `GCE_MIN_SCR_SIZE`, updates kernel metadata, starts setup-results/scratch/filestore scripts in parallel, writes `/var/www/varz` and hostname, exposes proc files and logs, removes one-time kernel/module objects, waits, installs syslog config, disables boot disk auto-delete, and runs post-setup hooks.

State and dependencies: `/results`, `/var/www`, `/run/test-env`, `/run/filestore-param`, setup marker files, GCE metadata, attached disks, syslog config, and hook directories. Depends on helper scripts in the same directory.

Integration points: consumes environment from `gce-load-kernel`, calls `gce-setup-results`, `gce-setup-scratch`, `gce-setup-filestore`, `gce-setup-pts`, and feeds shutdown/result collection.

Risks and test signals: many background jobs share failure handling through logs rather than immediate exit. Partition size computation is critical to test coverage. Integration tests should inspect created LVs/mounts, `/results/setup-syslog`, metadata, and reboot remount behavior.
