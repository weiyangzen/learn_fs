# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeChoosingPolicyFactory.java

Purpose: Creates configured `VolumeChoosingPolicy` instances and owns the shared lock used for committed-space reservation.

Important APIs and types: `getPolicy(ConfigurationSource)` reads `HDDS_DATANODE_VOLUME_CHOOSING_POLICY`, defaults to `CapacityVolumeChoosingPolicy`, and instantiates the policy reflectively with a `ReentrantLock`. `getVolumeSpaceReservationLock` exposes the same lock.

Control flow: Reflection constructs policies that accept a `ReentrantLock` constructor parameter. The static lock is process-wide for this factory.

State and persistence: The only state is static in-memory `LOCK`.

Dependencies and integration points: Used for normal container volume placement and by disk balancer's `ContainerChoosingPolicyFactory`, so balancing reservations and container-creation reservations share one synchronization mechanism.

Risks: Custom policies must provide the expected constructor signature. The static lock serializes reservation operations across all policy instances, which is simple but can reduce concurrency. Tests should cover default selection, configured class selection, constructor failure behavior, and lock identity sharing.
