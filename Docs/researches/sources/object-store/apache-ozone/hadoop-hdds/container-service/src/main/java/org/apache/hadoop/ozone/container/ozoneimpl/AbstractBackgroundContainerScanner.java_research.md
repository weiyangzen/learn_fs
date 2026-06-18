## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/AbstractBackgroundContainerScanner.java

Purpose: Base runnable for scheduled datanode container scanners, handling thread lifecycle, iteration cadence, pause/unpause, shutdown, and common metrics reset/logging.

Important APIs and functions: `start()` starts the daemon scanner thread. `run()` loops `runIteration()` until stopping and unregisters metrics on exit. `runIteration()` optionally scans, logs metrics, resets per-iteration gauges, and sleeps for the remaining interval. `scanContainers()` iterates containers and invokes subclass `scanContainer()`. `shutdown()`, `pause()`, `unpause()`, and `isAlive()` manage lifecycle.

Control flow and state: Atomic flags track stopping and pausing. Each iteration computes elapsed time and sleeps only the remaining configured interval. Interrupted scan operations set stopping. Subclasses supply container iterator, scan behavior, and metrics.

Persistence and dependencies: No direct persistence, but subclasses call container scan methods that can mark containers unhealthy or update checksums. Depends on `Container` and `AbstractContainerScannerMetrics`.

Risks: Any unchecked exception exits the scanner thread. Metrics are reset after every run-loop iteration, so consumers observe per-iteration gauges. Shutdown joins the thread and can block until scan code honors interruption. Pause only takes effect between container scans, not inside a long container scan.

Test signals: Start/run/shutdown behavior, pause skipping scans, interrupt handling, sleep duration calculation, metrics increment/reset/unregister, exception exit, and subclass scan invocation order.
