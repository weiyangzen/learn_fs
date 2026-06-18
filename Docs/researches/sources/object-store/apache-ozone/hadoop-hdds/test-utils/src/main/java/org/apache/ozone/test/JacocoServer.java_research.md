# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/JacocoServer.java

Purpose: `JacocoServer` is a simple TCP collector for JaCoCo remote coverage execution data. It accepts multiple agent connections and writes combined execution data to one `.exec` file.

Important APIs and types: It uses `ServerSocket`, `Socket`, `ExecutionDataWriter`, `RemoteControlReader`, `RemoteControlWriter`, `ISessionInfoVisitor`, and `IExecutionDataVisitor`. Static defaults are port `6300`, destination `/tmp/jacoco-combined.exec`, and a shared `lockMonitor`.

Control flow: `main` opens the destination file, starts a server socket, registers a shutdown hook to flush and close, then loops in `acceptConnections`. Each accepted socket is handled in a new thread. The handler wires reader visitors through synchronized wrappers, calls `reader.read()` until the remote stream ends, flushes the destination under the lock, and closes the socket.

State and persistence behavior: Persistent output is the combined JaCoCo exec file. Runtime state is the open server socket, destination writer, per-connection threads, and synchronized visitor access to avoid concurrent writes.

Dependencies and integration points: This utility integrates test JVMs using JaCoCo remote control with a centralized coverage file used by build or CI workflows.

Risks: Port and destination are hard-coded static fields, with no argument parsing. Handler threads are unmanaged and non-daemon by default. Exceptions print stack traces directly, and there is no graceful stop command beyond socket closure. `RemoteControlWriter` is constructed but not otherwise used.

Test signals: Successful server startup, accepted JaCoCo agent connections, nonempty combined exec output, and clean flush on shutdown.
