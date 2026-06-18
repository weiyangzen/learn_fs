# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/ContainerChoosingPolicyFactory.java

Purpose: Creates configured disk balancer `ContainerChoosingPolicy` instances.

Important APIs and types: `getDiskBalancerPolicy(ConfigurationSource)` reads `hdds.datanode.disk.balancer.container.choosing.policy`, defaults to `DefaultContainerChoosingPolicy`, and reflectively constructs the policy with a `ReentrantLock`.

Control flow: The factory passes `VolumeChoosingPolicyFactory.getVolumeSpaceReservationLock()` into the policy, sharing reservation synchronization with normal volume selection.

State and persistence: Stateless factory.

Dependencies and integration points: Used by `DiskBalancerService` during construction. Custom policies must implement `ContainerChoosingPolicy` and provide a matching constructor.

Risks: Reflection failures become service initialization failures. Tests should cover default class selection, configured policy class, constructor signature validation, and shared lock identity with normal volume choosing.
