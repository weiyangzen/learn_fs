# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerVersion.java

Purpose: Enumerates supported disk balancer info/config versions.

Important APIs and types: Currently defines `ONE(1, "First Version")`, `DEFAULT_VERSION`, a list of all values, and lookup helpers by int or string.

Control flow: Lookup methods linearly scan the immutable value list and return null when unsupported.

State and persistence: Version values are persisted in `diskBalancer.info` YAML and validated on read.

Dependencies and integration points: `DiskBalancerInfo` stores a version; `DiskBalancerYaml` writes and validates it.

Risks: Returning null on unknown versions means callers must check; `DiskBalancerYaml` does and throws `IOException`. Tests should cover known int/string lookup, unknown versions, and default version serialization.
