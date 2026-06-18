# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NetConstants.java

## Purpose
Defines constants and default `NodeSchema` instances for SCM network topology paths, costs, levels, and standard layers.

## Important APIs, Types, And Functions
Constants include path separator, reverse-scope prefix, root/default rack/nodegroup/datacenter/region strings, default costs, root level, and reusable schemas for root, region, datacenter, rack, nodegroup, and leaf.

## Control Flow
No executable flow beyond static initialization of schemas through `NodeSchema.Builder`.

## State And Persistence
Static constants only. Defaults influence runtime topology construction but are not persisted here.

## Dependencies And Integration Points
Depends on `NodeSchema.LayerType` and `StringWithByteString`. Integrated by topology normalization, placement policy, and schema loaders.

## Risks And Test Signals
Changing defaults alters placement compatibility. Tests should verify default schema order/costs, root/rack constants, and path separator assumptions.
