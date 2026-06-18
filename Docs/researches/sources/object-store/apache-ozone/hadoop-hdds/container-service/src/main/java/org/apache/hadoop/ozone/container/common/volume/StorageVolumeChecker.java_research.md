# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/StorageVolumeChecker.java

Purpose: Coordinates synchronous, asynchronous, and periodic disk health checks for datanode storage volumes. It detects failed volumes but leaves failure handling to the owning `VolumeSet`.

Important APIs and types: Uses `AsyncChecker<Boolean, VolumeCheckResult>` implemented by `ThrottledAsyncChecker`. Public APIs include `start`, `registerVolumeSet`, `checkAllVolumeSets`, `checkAllVolumes(Collection)`, `checkVolume(StorageVolume, Callback)`, `shutdownAndWait`, and testing accessors. The nested `ResultHandler` interprets future results.

Control flow: `start` schedules periodic scans. `checkAllVolumeSets` respects the minimum all-volume scan gap, updates background scanner metrics, and delegates to each registered volume set. `checkAllVolumes` schedules eligible checks, waits up to the configured timeout, snapshots completed healthy/failed sets under a result lock, and records timeout tolerance for pending volumes. `checkVolume` schedules one volume and calls a callback when complete.

State and persistence: Runtime state includes last full-scan timestamp, registered volume sets, executors, metrics, and the throttling delegate. No durable state is written.

Dependencies and integration points: `MutableVolumeSet` registers itself and calls checker methods. `StorageVolume.check` supplies actual health logic. Guava futures and callbacks manage asynchronous execution.

Risks: Correct timeout handling depends on distinguishing batch checks, where pending-volume timeout accounting happens in `checkAllVolumes`, from single-volume checks, where the callback records timeout failure. The `onFailure` interruption test checks `t instanceof InterruptedException`, while wrapped causes may differ. Tests should cover skipped recent checks, batch timeout tolerance, explicit failed results, single-volume callbacks, periodic metrics, and shutdown cancellation.
