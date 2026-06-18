# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMNodeInfo.java

## Purpose
Tests SCM high-availability node information extraction from `OzoneConfiguration`, including explicit HA service IDs, node IDs, addresses, and default ports.

## Important APIs, types, and functions
- Uses `SCMNodeInfo`, `OzoneConfiguration`, `ConfigurationException`, and `ScmConfigKeys`.
- Covers HA node info, default ports, missing SCM address validation, and non-HA REST/default behavior.
- Setup populates service and node configuration keys before each test.

## Control flow
The tests configure one or more SCM service/node entries, call SCM node-info builders, and assert the returned list contains expected host/port combinations or throws when required addresses are missing.

## State and persistence behavior
Configuration state is in-memory. It models persisted `ozone-site.xml` values without reading files.

## Dependencies and integration points
This is a guard for SCM HA bootstrap, node discovery, and address binding defaults.

## Risks and test signals
Bad config parsing can prevent SCM HA clusters from starting or bind them to wrong addresses. The tests signal defaults, required key validation, and non-HA compatibility.
