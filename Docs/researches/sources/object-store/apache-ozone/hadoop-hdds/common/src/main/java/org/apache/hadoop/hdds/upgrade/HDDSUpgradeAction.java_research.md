# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/upgrade/HDDSUpgradeAction.java

## Purpose
Marker interface for HDDS SCM and datanode upgrade actions.

## Important APIs and types
It extends `LayoutFeature.UpgradeAction<T>` and adds no methods.

## Control flow and state
No implementation behavior.

## Dependencies and integration points
`HDDSLayoutFeature` stores optional actions of this type. Concrete upgrade actions implement it to plug into the shared Ozone upgrade framework.

## Risks and test signals
No direct tests beyond ensuring concrete actions satisfy the inherited `UpgradeAction` contract.
