# sources/user-network-fs/blobfuse2/azure-pipeline-templates/e2e-tests-xload.yml

## Purpose
This template validates xload/preload behavior by comparing MD5 checksums from a normal file-cache mount and a read-only preload mount.

## Important APIs, Types, and Functions
It installs Python/JQ dependencies, generates configs with `azure_key.yaml` and `azure_key_xload.yaml`, uses `mount.yml`, `head`, `python3 testdata/scripts/generate-parquet-files.py`, `jq`, `md5sum`, and `diff`.

## Control Flow
The template installs dependencies, creates and mounts a normal read-write file-cache config, generates random files and parquet files on the mount, records MD5 sums, generates a preload config, mounts read-only, polls an `xload_stats_*.json` file until `PercentCompleted` is `100`, records MD5 sums again, unmounts, and diffs the two checksum files.

## State and Persistence Behavior
It writes generated data into the Azure container, checksum files in `$(WORK_DIR)`, xload stats JSON in `$(WORK_DIR)`, and logs/traces on failure.

## Dependencies and Integration Points
It is used by the nightly `XloadValidation` stage and depends on `jq`, Python data libraries, parquet generation script, and the stats manager output format.

## Risks and Edge Cases
The polling loop has no explicit timeout inside the shell step beyond job timeout. `ls $(WORK_DIR)/xload_stats_*.json` assumes one stats file exists. Diffing raw `md5sum` output can be sensitive to path/name differences.

## Test Signals
Signals include `PercentCompleted = 100`, matching MD5 output, successful read-only mount, and absence of failure logs/traces.
