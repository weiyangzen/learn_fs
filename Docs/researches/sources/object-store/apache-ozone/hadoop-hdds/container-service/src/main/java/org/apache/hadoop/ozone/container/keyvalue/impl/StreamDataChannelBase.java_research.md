## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/StreamDataChannelBase.java

Purpose: Provides the common file-backed `StateMachine.DataChannel` implementation for stream write channels, including file open/close, force, space checks, metrics, and cleanup lifecycle.

Important APIs and functions: The constructor opens the target block file as `RandomAccessFile("rw")`. `force()` syncs the file channel. `isOpen()` reports channel state. `assertSpaceAvailability()` validates requested bytes against the container volume. `setLinked()` marks the channel as attached to a committed block. `cleanUp()` invokes subclass cleanup if not linked. `writeFileChannel()` writes bytes and updates metrics and container stats.

Control flow and state: The base class tracks `linked` and `cleaned` atomically to avoid deleting or closing a channel that was successfully linked into the container. Subclasses supply the operation type and cleanup body. I/O exceptions call `checkVolume()`, which reports the volume through `StorageVolumeUtil.onFailure()`.

Persistence and dependencies: This class writes to the local block file and updates `ContainerData.updateWriteStats()` plus `ContainerMetrics` byte and latency counters. It depends on Ratis `StateMachine.DataChannel`, Ozone `ContainerData`, volume failure utilities, and Hadoop monotonic time.

Risks: Cleanup semantics depend on `setLinked()` being called by higher-level code at the right time. Space checks are performed before writes but cannot prevent concurrent exhaustion. Metrics update after each low-level write uses the actual byte count; zero or negative writes are handled by subclass loops. Failure handling marks the whole volume suspect on I/O errors.

Test signals: Cover constructor failure for missing files, `force()` error paths, linked versus unlinked cleanup, repeated cleanup calls, write metrics/stat updates, volume failure signaling on exceptions, and close idempotency through subclasses.
