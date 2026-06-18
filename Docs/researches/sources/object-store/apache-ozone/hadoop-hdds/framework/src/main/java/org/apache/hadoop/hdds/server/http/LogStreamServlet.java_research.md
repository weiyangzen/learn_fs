# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/LogStreamServlet.java

Purpose: `LogStreamServlet` streams current Log4j root logger output to an HTTP response for live diagnostics.

Important APIs/types/functions: `doGet()` creates a `WriterAppender` using pattern `%d [%p|%c|%C{1}] %m%n`, sets threshold TRACE, adds it to the root logger, sleeps until interrupted, and removes the appender in `finally`.

Control flow: requests attach a writer-backed appender to the global root logger. The servlet thread blocks for a very long sleep, so the connection remains open while logs are written to the response. On interruption or completion, the appender is removed.

State and persistence: no servlet fields; transient appender attached to global Log4j state. No persistence.

Dependencies/integration: added by `BaseHttpServer` as `/logstream` when default Ozone apps are enabled. Depends on Log4j 1.x APIs and servlet response writer.

Risks: each request can hold a servlet thread indefinitely. Access control is whatever normal servlet filters provide; exposing logs can leak sensitive operational details if not protected. Writer failures rely on appender behavior.

Test signals: no direct test was found for this servlet; integration is through `BaseHttpServer` default servlet registration.
