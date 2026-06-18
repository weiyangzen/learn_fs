# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/TrashPolicyOzone.java

Purpose: `TrashPolicyOzone` specializes Hadoop trash behavior for OM. It uses an Ozone-aware filesystem and a multithreaded emptier to checkpoint current trash directories and delete expired checkpoints.

Important APIs and types: It extends `OzoneTrashPolicy`, overrides `initialize` and `getEmptier`, and defines an inner `Emptier`. Private methods `createCheckpoint`, `deleteCheckpoint`, and `getTimeFromCheckpoint` implement checkpoint lifecycle. It uses `OMClientConfig` for trash emptier pool size and OM metrics for activity/failure counters.

Control flow: Initialization chooses an Ozone-specific checkpoint interval with fallback to Hadoop's config and clamps negative deletion interval to zero. The emptier sleeps until the next interval boundary, skips work unless OM leader is ready, lists all trash roots, creates a new `TrashPolicyOzone` per root, and submits a task that deletes expired checkpoints then renames `Current` to a timestamped checkpoint. Checkpoint creation retries suffixes up to 1000 times on name collision.

State and persistence behavior: Durable state is trash checkpoint directories under each trash root. Runtime state includes the configured intervals and a fixed-size executor. Date formats are static and synchronized for thread safety.

Dependencies and integration points: It integrates with `TrashOzoneFileSystem`, OM leadership, OM metrics, Hadoop `TrashPolicy`, and Ozone client configuration.

Risks and test signals: It only runs on a leader-ready OM, so leadership transitions affect cleanup latency. The executor queue can run tasks in the caller when saturated. Tests should cover interval fallback, disabled trash, checkpoint collision retries, old-format checkpoint parsing, deletion cutoff boundaries, leader skip behavior, executor shutdown on interrupt, and metrics on success/failure.
