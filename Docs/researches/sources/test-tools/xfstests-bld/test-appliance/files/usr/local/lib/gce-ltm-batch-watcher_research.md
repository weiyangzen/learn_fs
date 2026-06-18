# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-ltm-batch-watcher

Purpose: long-running appliance loop that watches a GCS batch command directory and executes queued shell fragments through `gce-run-batch`.

Important flow: set a GCE/xfs-friendly PATH, source `gce-funcs`, read `ltm_wait` metadata, then loop forever. Each iteration runs `script -c "/usr/local/lib/gce-run-batch --gce-dir ltm-batch"` into a temporary transcript, uploads that transcript to `gs://$GS_BUCKET/ltm-batch.log`, removes the local file, and either blocks on metadata change via `wait_for_change=true` or sleeps for 60 seconds.

State and dependencies: uses `/run/ltm-batch.$$` as transient log state and GCS `ltm-batch.log` as persistent operational evidence. It depends on metadata service semantics, `script`, `gcs_cp`, and `gce-run-batch`.

Integration points: used for remote administrative or scheduled commands against LTM machines. It shares batch directory semantics with `gce-run-batch`.

Risks and test signals: command execution is intentionally privileged and trusts GCS batch contents. A failure in `gce-run-batch` does not break the infinite loop. Test evidence is the uploaded transcript and deletion of processed batch objects when `gce-run-batch` is not in keep mode.
