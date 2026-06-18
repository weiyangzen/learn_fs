<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/heal_erasure_disk_rebuild_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/heal_erasure_disk_rebuild_test.rs

Purpose: this module tests erasure-set healing by deliberately wiping or replacing disk directories and verifying RustFS rebuilds object metadata and preserves readable object bodies. It covers single-node runtime wipe auto-heal, single-node restart plus admin deep heal, and multi-node remote disk replacement.

Important APIs, types, and functions: `has_file_under()` recursively detects any file in a disk path. `object_metadata_exists_on_disk()` checks `bucket/key/xl.meta`. `assert_object_body()` reads an object through S3 and compares bytes. Tests use `RustFSTestEnvironment`, `RustFSTestClusterEnvironment`, `start_rustfs_server_with_env()`, cluster node stop/start helpers, `execute_awscurl()` for admin heal/status, `HashSet` tracking of rebuilt keys, and `tokio::time::{sleep, timeout}`.

Control flow: the runtime-wipe test creates four disk dirs, starts RustFS with three explicit paths and one implicit path plus a short heal interval, uploads several objects, wipes `disk0` while the server keeps running, then polls until every `xl.meta` reappears and `format.json` is restored. The deep-heal test writes objects including non-ASCII/symbol keys, stops the server, wipes `disk0`, restarts, posts a recursive heal request, and polls for metadata rebuild before final body checks. The cluster test starts four nodes, writes one object, stops node 1, wipes its data dir, writes another object while the node is down, restarts it, checks background-heal status accepts no explicit content length, posts admin heal, and polls until both keys are rebuilt on the replaced remote disk.

State and persistence: these tests manipulate real filesystem state under temporary disk roots, RustFS erasure metadata (`xl.meta`), `.rustfs.sys/format.json`, object shards, and cluster/node lifecycle. Environment variables tune bypass disk checks, heal intervals, scanner/heal enablement, object counts, and timeouts.

Dependencies and integration points: depends on local filesystem permissions, RustFS erasure coding layout, admin heal API, cluster harness, AWS SDK object operations, and `awscurl` execution. It integrates scanner/background heal, foreground admin heal, disk-format restoration, and object read quorum.

Risks: tests are slow and timing-sensitive, with default polling windows of 45, 60, and 90 seconds. Directly checking `xl.meta` couples the tests to storage layout. Runtime disk removal can race with background IO. Non-ASCII key coverage is valuable but depends on platform path handling. Admin heal acceptance is checked, but detailed heal progress response semantics are not parsed.

Test signals: passing tests show objects remain readable during/after disk loss, wiped disks regain `xl.meta` for every expected key, format metadata is restored after runtime wipe, admin deep heal can rebuild after restart, remote replacement heals both pre-outage and outage-written objects, and background-heal status does not fail with `MissingContentLength`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/heal_erasure_disk_rebuild_test.rs -->
