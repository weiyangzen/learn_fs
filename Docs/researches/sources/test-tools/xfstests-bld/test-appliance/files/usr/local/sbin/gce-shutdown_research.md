# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/gce-shutdown

Purpose: finalizes a GCE test VM by summarizing results, sending emails, uploading result artifacts, cleaning Filestore state, running shutdown hooks, and deleting or powering off the instance.

Important flow: skip image-build instances; enforce singleton; handle self-shutdown marker; if results exist and shutdown reason is not abort, stop tests, append shutdown reason, copy xUnit results, handle timeout missing-END/error cases, generate xfstests or blktests summary/failures, optionally upload summary, choose report/failure/JUnit recipients from metadata, send SendGrid mail through `send-mail.py`, tar/xz `/results`, and upload results tarball and XML to GCS. Then remove Filestore per-instance directories and possibly delete Filestore, run shutdown hooks, log shutdown, and either power off or delete the VM.

State and dependencies: `/results`, `/tmp/results.xml`, GCS result objects, GCE metadata, Filestore directories, `/run` markers, SendGrid credentials, `gen_results_summary`, `gce-logger`, `gcs_cp`, and `gcloud`.

Integration points: LTM shards poll for result tarballs uploaded here. `gce-setup-filestore` writes parameters consumed here. `gce-logger` metadata updates help LTM monitoring.

Risks and test signals: shutdown is dense and mostly best-effort; failures late in upload/email can lose diagnostics. Regex summaries need maintenance with xfstests/blktests output changes. Integration tests should validate normal, timeout, abort, power-button, and Filestore cleanup paths.
