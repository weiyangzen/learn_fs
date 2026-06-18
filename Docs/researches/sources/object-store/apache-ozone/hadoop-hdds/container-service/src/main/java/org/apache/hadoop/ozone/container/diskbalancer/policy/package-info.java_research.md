# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ozone.container.diskbalancer.policy` as the package containing policy classes for the DiskBalancer service. It does not define runtime code, but it anchors Javadoc and package-level ownership for disk-balancer selection policies.

## Important APIs and Types
There are no functions or classes in this file. The relevant exported types in the package include `ContainerChoosingPolicy`, `ContainerCandidate`, and `DefaultContainerChoosingPolicy`.

## Control Flow
No control flow is present. Runtime behavior is implemented by classes in the package, especially the default policy that chooses source/destination volumes and containers.

## State and Persistence
No state is held or persisted. The file only supplies package documentation.

## Dependencies and Integration Points
It integrates with Java package documentation and the disk-balancer implementation by declaring the package. Its practical integration point is indirect: classes in this package are loaded by `ContainerChoosingPolicyFactory` and `DiskBalancerService`.

## Risks and Test Signals
The only material risk is documentation drift: the package currently contains policy classes and the description remains accurate. There is no direct test coverage needed for this descriptor; behavioral tests belong to package classes such as `TestDefaultContainerChoosingPolicy`.
