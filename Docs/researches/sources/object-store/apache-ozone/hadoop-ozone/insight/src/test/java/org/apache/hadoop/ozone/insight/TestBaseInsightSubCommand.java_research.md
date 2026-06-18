<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestBaseInsightSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestBaseInsightSubCommand.java

Purpose: unit tests for HTTP/HTTPS host resolution in `BaseInsightSubCommand`.

Important APIs: tests `getHost` for HTTP_ONLY SCM/OM configured HTTP addresses, HTTPS_ONLY configured HTTPS addresses, HTTP_AND_HTTPS preference for HTTPS, and fallback from wildcard HTTP/HTTPS bind addresses to SCM/OM RPC hostnames with default web ports.

Control flow and test signals: builds fresh `OzoneConfiguration` instances with specific keys and asserts exact URL strings. It confirms SCM and OM fallback behavior and scheme selection.

State and persistence: no external state.

Dependencies and integration: Ozone/SCM/OM config constants and JUnit 5.

Risks and gaps: does not test explicit `Component` hostname/port, unsupported component types, malformed addresses, IPv6, or absent ports. It also does not verify that `getInsight` resolves all registered names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestBaseInsightSubCommand.java -->
