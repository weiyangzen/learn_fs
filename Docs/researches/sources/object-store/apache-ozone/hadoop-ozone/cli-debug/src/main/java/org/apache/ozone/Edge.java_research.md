# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/ozone/Edge.java

Purpose: `Edge` customizes graph rendering by suppressing edge labels in generated compaction DAG images.

Important APIs and types: It extends JGraphT `DefaultEdge` and overrides `toString` to return an empty string.

Control flow and state: There is no state beyond `DefaultEdge` internals. Rendering code uses the string representation as the label.

Dependencies and integration points: `PrintableGraph` uses `DefaultDirectedGraph<String, Edge>` so PNG output does not show source/target text on edges.

Risks and test signals: Behavior is intentionally minimal. Tests can assert `new Edge().toString().isEmpty()` indirectly through clean graph render labels if image inspection is available.
