## sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/generate_folders_and_files.py

Purpose: Creates and validates GCS folder/file structures for HNS rename benchmarks.

APIs and control flow: Key helpers validate config consistency, list GCS directories via `gcloud alpha storage ls`, compare folder/file counts, delete existing bucket data, generate sparse files in batches, upload with `gcloud storage cp`, create top-level and nested folder structures, and delete the temp directory. Main checks gcloud, loads JSON, validates, compares existing bucket structure, deletes mismatched content, and regenerates data.

State and persistence: Writes temp files under `./tmp/data_gen`, timestamped `.out` logs, and GCS objects. It may delete all existing objects under the configured bucket.

Dependencies and risks: Heavy shell use with `shell=True`; upload uses `Popen(...).communicate()` but does not inspect return code, so some upload failures may be missed. Broad `except` blocks hide specific listing errors. `--keep_files` is parsed but not used.

Test signals: Unit tests cover config validation, listing, structure comparison, deletion, generation/upload happy and failure paths, and directory parsing.
