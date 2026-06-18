# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementCapacity.java

Purpose: This test checks that the capacity-biased placement policy excludes used nodes and nodes without sufficient free space, while favoring nodes with more available capacity over many selections.

Important APIs and types: It uses `SCMContainerPlacementCapacity`, `SCMContainerPlacementMetrics`, `NodeManager`, `DatanodeInfo`, `SCMNodeMetric`, storage and metadata reports, `OzoneConfiguration`, and `OZONE_DATANODE_RATIS_VOLUME_FREE_SPACE_MIN`.

Control flow: The test creates seven healthy datanodes with 100-byte capacity, modifies three storage reports to lower remaining space, mocks `NodeManager.getNodes`, `getNodeStat`, and `getNode`, constructs the capacity policy, and repeatedly requests one target while two existing nodes are excluded. It counts how often each selected datanode appears over 1000 iterations.

State and persistence behavior: There is no persistence. Runtime state is datanode storage report data, mocked node metrics, exclusion list, and selection count map.

Dependencies and integration points: The policy relies on SCM node metrics and storage-report-derived node details. It is used when SCM wants probability-weighted target selection by free capacity rather than pure random selection.

Risks: The final distribution assertions are probabilistic and may be sensitive to random selection implementation or sample size. The test uses tiny byte-scale capacities, which is efficient but can obscure real-world unit behavior. Metadata-space filtering is present through reports but not deeply varied.

Test signals: Every iteration returns exactly one node, excludes the two existing nodes, excludes the low-space node, and selects high-capacity nodes more often than nodes with less remaining space.
