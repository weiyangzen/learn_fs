# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/pts-save

Purpose: saves Phoronix Test Suite state and/or results from a GCE PTS instance back to GCS.

Important flow: source `gce-funcs`, parse flags such as `--state` and `--results`, package `/pts` or `/var/lib/phoronix-test-suite` content into `.tar.xz`, and upload to bucket names used by `gce-setup-pts` for later restoration.

State and dependencies: reads PTS data directories, writes temporary tarballs, uploads `pts-state.tar.xz`, `pts-results.tar.xz`, or per-instance result archives to `gs://$GS_BUCKET`. Depends on tar/xz and GCS helpers.

Integration points: paired with `gce-setup-pts`, which restores these archives at setup time.

Risks and test signals: large result archives can be expensive and partial uploads can leave stale state. Tests should validate flag selection and archive path compatibility with restore logic.
