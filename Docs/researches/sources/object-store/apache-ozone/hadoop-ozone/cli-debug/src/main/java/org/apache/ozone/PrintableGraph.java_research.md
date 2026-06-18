# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/ozone/PrintableGraph.java

Purpose: `PrintableGraph` converts a Guava `MutableGraph<CompactionNode>` into a JGraphT graph and writes a hierarchical PNG image.

Important APIs and types: Constructor accepts a Guava graph and `GraphType`. Public methods are `generateImage` and `getGraph`. It uses `DefaultDirectedGraph`, `JGraphXAdapter`, `mxHierarchicalLayout`, `mxCellRenderer`, `ImageIO`, `CompactionNode`, and custom `Edge`.

Control flow: Construction calls `getGraph`, which adds vertices for every compaction node and directed edges for every Guava edge. `generateImage` rejects an empty graph, lays out the JGraphX adapter hierarchically, renders a white-background image at scale 2, and writes it as PNG.

State and persistence behavior: Runtime state is the converted JGraphT graph. Persistent output is the image file path supplied by the caller.

Dependencies and integration points: `CompactionLogDagPrinter` uses this wrapper to render OM compaction DAGs. `TestPrintableGraph` validates empty and non-empty graph outputs for all graph type labels.

Risks: Vertex labels can collide when graph type reduces nodes to equal strings, causing merged vertices. Image generation depends on AWT/ImageIO availability. `generateImage` writes directly to the requested path without creating parent directories.

Test signals: Existing tests cover empty graph error and file creation for all `GraphType` values. Additional tests could assert vertex labels and edge count in `getGraph`.
