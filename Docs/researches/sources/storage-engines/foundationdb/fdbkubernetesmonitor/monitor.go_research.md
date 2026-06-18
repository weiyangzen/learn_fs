# sources/storage-engines/foundationdb/fdbkubernetesmonitor/monitor.go

Purpose: implements the Kubernetes monitor process supervisor. It reads JSON process configuration, chooses the correct fdbserver binary, starts and restarts configured subprocesses, exposes metrics/pprof, watches local files, reacts to pod annotations, and coordinates shutdown.

Important APIs and types: `monitor` stores config file path, current container version, custom environment, active configuration bytes, last config time, process count/PIDs, mutex, pod client, logger, and metrics. `startMonitor` creates the pod client and HTTP server. Core methods include `readConfiguration`, `loadConfiguration`, `acceptConfiguration`, `runProcess`, `processRequired`, `processIsIsolated`, `watchConfiguration`, `handleFileChange`, `signalProcesses`, `run`, and `watchPodTimestamps`.

Control flow: startup creates Kubernetes watches, starts timestamp handling, registers metrics, starts HTTP/HTTPS metrics serving, then enters `run`. Config loads validate binary executability, node-label environment, generated arguments, and isolate annotation. Accepted configs spawn per-process loops. Each loop generates arguments, starts `exec.Cmd`, streams stdout/stderr to logs, waits, records exit, and backs off on non-zero exits.

State and persistence behavior: process IDs and active config are in-memory and mutex-protected. Persistent side effects are subprocesses, Kubernetes annotations, and cluster-file change annotations. File watches cover the monitor config and `/var/fdb/data/fdb.cluster`.

Dependencies and integration points: integrates with API config types, Kubernetes client, certloader, Prometheus, fsnotify, OS process/signal APIs, and the fdbserver binary layout.

Risks: long-running paths have race and lifecycle complexity. HTTPS startup logs and exits on `ListenAndServeTLS`, but if TLS is configured the following plain HTTP call is still lexically reachable after TLS returns. `readConfiguration` logs `err` when version is nil even though `err` may be nil. Cluster-file watch waits indefinitely for file creation.

Test signals: `monitor_test.go` covers node-label env injection, backoff math, config parsing, binary path selection, and isolate annotation. The full process loop, HTTP server, fsnotify paths, and shutdown delay are not directly exercised.
