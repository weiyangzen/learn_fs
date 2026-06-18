## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/BlockDeletingServiceTestImpl.java

Purpose: `BlockDeletingServiceTestImpl` is a test-only subclass of `BlockDeletingService` that makes block deletion execution manually triggerable and observable.

Important APIs and types: constructor wires the superclass with zero service timeout, millisecond units, a batch limit of `10`, and a new `ContainerChecksumTreeManager`. Test APIs are `runDeletingTasks()`, `isStarted()`, and `getTimesOfProcessed()`.

Control flow and state: `start()` launches a daemon testing thread that repeatedly creates a `CountDownLatch`, waits for `runDeletingTasks()` to count it down, submits one `PeriodicalTask` to the executor, waits up to three seconds, and increments `numOfProcessed` on success. `shutdown()` interrupts the testing thread and delegates to superclass shutdown.

Persistence and integration: actual deletion persistence comes from inherited `BlockDeletingService` behavior against `OzoneContainer`; this subclass only controls scheduling. It integrates checksum tree updates by constructing a manager for the superclass.

Risks and test signals: `runDeletingTasks()` throws if the latch is already zero, preventing double triggers for one cycle. If the task fails or times out, the test thread returns and stops processing further triggers. It is package-private and intentionally limited to tests.
