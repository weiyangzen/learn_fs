# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/test/java/org/apache/hadoop/ozone/freon/containergenerator/TestGeneratorDatanode.java

Purpose: JUnit test coverage for `GeneratorDatanode.getPlacement`.

Important APIs/types/functions: test methods `testPlacementSinglePipeline`, `testPlacement10Nodes`, `testPlacement10NodesOverlap`, and helper `compare`.

Control flow: each test invokes `compare`, which builds a `HashSet` from expected datanode indexes and asserts equality with the set returned by `getPlacement(containerId, maxDatanodes, overlap)`.

State/persistence: none.

Dependencies/integration: JUnit Jupiter assertions and `GeneratorDatanode`.

Risks: covers representative happy paths only. It does not validate invalid `maxDatanodes`, overlap values outside documented bounds, modulo behavior for larger ids, or actual datanode container file generation.

Test signals: confirms one-based datanode placement for 3-node single pipeline, repeated grouping for 10 nodes with overlap 1, and shifted overlapping groups for overlap 2.
