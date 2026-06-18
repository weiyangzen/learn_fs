## sources/user-network-fs/gcsfuse/perfmetrics/scripts/generate_files.py

Purpose: Generates batches of sparse local files and uploads them to a GCS bucket according to an INI config.

APIs and control flow: `logmessage` appends to a timestamped output file and logs to stdout. `generate_files_and_upload_to_gcs_bucket` batches by `BATCH_SIZE=100`, creates sparse files using `truncate` based on b/KB/MB/GB units, optionally uploads with `gcloud storage cp --recursive`, copies files to a local bucket-shaped folder, deletes temp batch files, and logs progress. Main parses `config_file` and `--keep_files`, checks gcloud, reads config sections, creates local directories, uploads each section, and deletes local/temp folders unless kept.

State and persistence: Writes sparse files under `./tmp/data_gen`, local bucket directories, timestamped `.out` log, and GCS objects.

Dependencies and risks: Uses shell commands for gcloud/cp/rm and drops into an interactive shell on errors. File-size parsing assumes two-character units, so `1b` is problematic.

Test signals: No tests in this subset; operational progress appears in the output log.
