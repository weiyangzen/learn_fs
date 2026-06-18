# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/ProfileServlet.java

Purpose: `ProfileServlet` exposes async-profiler through the Ozone HTTP server. It starts profiler runs for a target JVM process and serves completed profile files.

Important APIs/types/functions: constructor resolves `ASYNC_PROFILER_HOME` or `async.profiler.home`, resolves PID from `JVM_PID` or runtime MXBean, and creates `OUTPUT_DIR`. `doGet()` validates profiler availability, handles `file` downloads, parses query parameters, acquires a lock, builds a `profiler.sh` command, starts it asynchronously, and responds with auto-refresh. `doGetDownload()` validates filenames and streams completed files. `generateFileName()` and `validateFileName()` are visible for tests. Enums `Event` and `Output` map supported profiler events/output formats.

Control flow: a request without `file` starts a profile if no profiler process is alive and the lock is acquired within 3 seconds. It writes output into `java.io.tmpdir/prof-output-ozone` with a constrained filename pattern and responds `202 Accepted` plus a `Refresh` header. A request with `file` validates the filename, returns an auto-refresh page while the file is short/incomplete, then streams HTML/SVG/tree or raw output.

State and persistence: servlet fields hold profiler home, PID, lock, and current `Process`. Profile artifacts persist under the temp output directory until cleaned externally.

Dependencies/integration: optionally added by `BaseHttpServer` at `/prof` when profiler support is enabled. Depends on async-profiler shell script, servlet APIs, Apache Commons IO/Lang, JVM management APIs, and OS/kernel profiler permissions.

Risks: powerful diagnostic endpoint; `BaseHttpServer` logs a production warning when enabled. Query parameters are intentionally limited but still execute an external command. File download safety depends on the strict filename regex. Only one profiler run per servlet instance is allowed at a time.

Test signals: `TestProfileServlet` validates generated filenames and rejects path traversal/newline filename attempts. Operational behavior is integration-dependent because it requires async-profiler and OS settings.
