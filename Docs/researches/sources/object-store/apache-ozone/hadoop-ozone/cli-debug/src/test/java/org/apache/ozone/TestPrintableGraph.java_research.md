# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/ozone/TestPrintableGraph.java

Purpose: `TestPrintableGraph` verifies PNG generation behavior for `PrintableGraph` across all graph label modes.

Important APIs and types: It uses mocked Guava `MutableGraph<CompactionNode>`, parameterized JUnit tests over `PrintableGraph.GraphType`, temp directories, and Mockito.

Control flow: The empty-graph test constructs a graph with no mocked nodes and expects `generateImage` to throw `IOException` with `Graph is empty.`. The non-empty test stubs four `CompactionNode`s, generates an image for each graph type, and asserts the output path exists.

State and persistence behavior: It writes generated image files under a JUnit temp directory and uses no other persistence.

Dependencies and integration points: It covers the graph helper used by OM compaction DAG rendering.

Risks: The non-empty test stubs nodes but not edges, so it verifies vertex-only rendering but not edge conversion. It does not inspect image content.

Test signals: Empty graph message and file existence for `FILE_NAME`, `KEY_SIZE`, and `CUMULATIVE_SIZE`.
