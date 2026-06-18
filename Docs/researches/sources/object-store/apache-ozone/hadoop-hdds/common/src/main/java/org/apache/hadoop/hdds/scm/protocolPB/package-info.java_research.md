# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/package-info.java

## Purpose
Documents the package as containing client-side classes for the storage container protocol.

## Important APIs and types
No executable APIs are defined here. In this subset, `ContainerCommandResponseBuilders` and `OzonePBHelper` are the concrete protocol helper classes.

## Control flow, state, and persistence
There is no runtime behavior or persistence.

## Dependencies and integration points
The package sits at the boundary between SCM/client code and protobuf container protocol messages.

## Risks and test signals
No direct test requirements. Documentation should stay aligned with package contents if server-side-only helpers are added.
