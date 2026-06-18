# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ReplicasVerify.java

Purpose: `ReplicasVerify` implements `ozone debug replicas verify`, a live-cluster command that scans keys under a key, bucket, volume, or all volumes and runs selected replica verification checks.

Important APIs and types: It extends shell `Handler`, mixes in `ScmOption` and `ShellReplicationOptions`, accepts an Ozone URI, `--all-results`, grouped verification flags `--checksums`, `--block-existence`, `--container-state`, and `--container-cache-size`. It uses `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `OzoneKey`, `OmKeyInfo`, `OmKeyLocationInfo`, `ReplicaVerifier`, `JsonUtils`, counters, and a shutdown hook.

Control flow: `execute` determines verification scope from URI depth, constructs the requested verifier list, registers a shutdown hook, then calls `findCandidateKeys`. The scan walks the addressed key, bucket, volume, or all volumes; directory marker keys ending in `/` are skipped. `processKey` fetches key info from OM, filters by replication options, iterates latest block locations, iterates each pipeline datanode, runs every verifier, writes nested JSON for blocks/replicas/checks, aggregates failed verification types, and includes the key only if it failed or `--all-results` is set.

State and persistence behavior: The command does not mutate Ozone. Runtime state includes counters for processed volumes, buckets, keys, passed/failed keys, per-type failure counters, start/end times, selected verification types, and any thrown exception. It prints JSON to stdout and summary information to stderr through the shutdown hook.

Dependencies and integration points: It integrates Ozone shell address parsing, OM key lookup, SCM/datanode clients through verifier implementations, replication filters, and the global shutdown hook manager.

Risks: If no verification flag is supplied, the arg group may still allow an empty verifier list depending on picocli binding; keys would pass without checks. Full namespace scans can be expensive and network-heavy. The shutdown hook may print summaries on normal JVM exit as well as interruption. EC/Ratis filtering requires exact replication type and factor match.

Test signals: Useful tests cover scope selection, replication filtering, key/bucket/volume/all-volumes walking, directory-marker skip, JSON pass/fail structure, summary counters, all-results behavior, per-type failure counting, verifier exception propagation, and shutdown-hook summary timing.
