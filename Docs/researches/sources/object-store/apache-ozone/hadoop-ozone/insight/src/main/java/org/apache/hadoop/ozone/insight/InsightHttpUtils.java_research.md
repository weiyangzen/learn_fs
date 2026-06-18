<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/InsightHttpUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/InsightHttpUtils.java

Purpose: static utility for Insight HTTP/HTTPS calls, including SPNEGO-aware connection creation and UTF-8 response reading.

Important APIs: `isSpnegoEnabled(conf)` treats `ozone.http.security.enabled` values `kerberos` or `true` as SPNEGO. `openConnection(url, conf)` creates a Hadoop `URLConnectionFactory` and opens a `HttpURLConnection` with SPNEGO toggle; connection refusal and authentication failure are converted to stderr messages plus null return, while other exceptions become `IOException`. `readResponse` validates HTTP 200 and joins the full response body. `getResponseReader` validates HTTP 200 and returns a streaming `BufferedReader`.

Control flow and integration: metrics and log subcommands call `openConnection` for `/prom`, `/logstream`, and `/logLevel`. `LogSubcommand` owns closing the streaming reader. `MetricsSubCommand` reads a complete Prometheus page into memory.

State and persistence: stateless. No persistence.

Risks and tests: callers must handle null returns from connection/auth failures; current callers usually rethrow runtime exceptions. Full response reading can be expensive if `/prom` grows large, though acceptable for diagnostics. Authentication detection is string-based and tightly coupled to Ozone config semantics. No direct tests cover SPNEGO, non-200 responses, or stderr behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/InsightHttpUtils.java -->
