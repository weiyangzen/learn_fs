# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/shard.go

Purpose: manages one GCE test VM shard from launch through monitoring, result retrieval, classification, and cleanup.

Important type/API: `ShardWorker` stores shard identity, VM command args, status tracking, timeout/reset state, log paths, result names, and unpacked result directory. Key methods are `Run`, `monitor`, `updateSerialData`, `shutdownOnTimeout`, `finish`, `getResults`, `Info`, and `exit`.

Control flow: `NewShardWorker` builds a `gce-xfstests` command with instance name, zone, bucket, kernel, bucket subdir, config, arch options, image project defaults, no-email, and default `--no-vm-timeout`. `Run` launches the command with `check.LimitedRun`, then `monitor` polls Compute instance state, serial output, and metadata status. If status stalls beyond `monitorTimeout`, it resets the VM; launch timeouts or repeated reset failures classify as errors. `finish` finds result tarballs in GCS, runs `gce-xfstests get-results`, checks reboot markers, deletes shard result/summary objects, and updates status.

State and dependencies: GCE instance metadata/status, serial output log, command log, local unpacked results, GCS result objects, and `ShardScheduler` GCP client. Depends on Compute API, `gce-xfstests`, `results_no_reboots`, `tar` extraction performed by external script, and logrus.

Risks and test signals: metadata status is the heartbeat, so logger failures can cause resets. Serial output offset gaps are recorded but not recovered. Result lookup retries are fixed. Tests should mock GCP instance states, metadata transitions, missing tarballs, and timeout classification.
