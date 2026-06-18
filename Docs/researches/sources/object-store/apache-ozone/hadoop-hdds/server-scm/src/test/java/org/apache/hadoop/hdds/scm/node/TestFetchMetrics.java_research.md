# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestFetchMetrics.java

Purpose: smoke tests for `FetchMetrics`, verifying metrics JSON retrieval returns a payload containing a `beans` field for unfiltered and filtered JMX queries.

Important APIs and types: a static `FetchMetrics` instance calls `getMetrics(null)` and `getMetrics("Hadoop:service=StorageContainerManager,name=NodeDecommissionMetrics")`. Tests use regex `Pattern.compile("beans", Pattern.MULTILINE)` and assert a match.

Control flow: both tests are straight-line fetch/regex/assert paths. They do not parse JSON structurally.

State and persistence: no persistence. It depends on the JVM's metrics/JMX infrastructure available during tests.

Integration points and risks: provides a low-cost signal that metrics fetch plumbing returns JMX-like output. Because it only searches for the word `beans`, it does not validate the requested bean exists, specific metrics are present, or malformed filters fail correctly.
