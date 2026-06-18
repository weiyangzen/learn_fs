# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-run-batch

Purpose: downloads and runs queued shell script fragments from a GCS batch directory.

Important flow: source GCE/test config, parse `--keep` and `--gce-dir`, sync `gs://$GS_BUCKET/$GCE_DIR` to `/run/batch-cmds`, iterate sorted files, optionally delete the remote object before execution, run each file under `/bin/bash -vx` via `script -a` into `/var/log/gce-run-batch.log`, and remove the local command file.

State and dependencies: uses `/run/batch-cmds`, `/var/log/gce-run-batch.log`, and GCS objects. It depends on `gcs_rsync`, `gcs_rm`, `script`, and Bash.

Integration points: driven by `gce-ltm-batch-watcher` for LTM command processing.

Risks and test signals: executing trusted bucket content as root is powerful; deleting before execution means failed commands are not retried unless `--keep` is set. Tests should check sorting, deletion semantics, option parsing, and transcript append behavior.
