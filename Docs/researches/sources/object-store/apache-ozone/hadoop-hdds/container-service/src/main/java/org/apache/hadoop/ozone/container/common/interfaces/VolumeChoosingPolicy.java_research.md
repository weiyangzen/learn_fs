<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/VolumeChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/VolumeChoosingPolicy.java

Purpose: policy interface for choosing a datanode volume to store a new container replica.

Important APIs and control flow: `chooseVolume` receives a list of available `HddsVolume` instances and the maximum container size, and returns a selected volume or throws `IOException` when disks are unavailable or full. The interface declares that implementations must be thread-safe.

State and persistence: interface only. Implementations may maintain counters or random state but must guard them for concurrent container creation.

Dependencies and integration: used by `Container.create` implementations and handlers during container placement.

Risks and test signals: tests for implementations should cover empty lists, failed/full volumes, reserved-space constraints, fairness or ordering policy, concurrent calls, and max-size overflow/edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/VolumeChoosingPolicy.java -->
