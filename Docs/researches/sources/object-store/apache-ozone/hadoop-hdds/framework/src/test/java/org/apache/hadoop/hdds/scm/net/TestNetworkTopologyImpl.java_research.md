# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestNetworkTopologyImpl.java

## Purpose

This large test suite validates `NetworkTopologyImpl` behavior across multiple topology schemas, including membership, path resolution, add/remove/update, random selection under scopes and exclusions, affinity selection, distance costs, sorting, and ancestor/descendant helpers.

## Important APIs, Types, And Functions

Key production APIs are `NetworkTopology.add`, `remove`, `update`, `contains`, `getNode`, `chooseRandom`, `getNumOfLeafNode`, `getNumOfNodes`, `getNodes`, `isSameParent`, `isSameAncestor`, `getDistanceCost`, `sortByDistanceCost`, `NodeSchemaManager.init`, `NodeImpl`, and `InnerNodeImpl`. Helpers `topologies`, `initNetworkTopology`, `pickNodesAtRandom`, and `pickNodes` generate broad coverage.

## Control Flow

Parameterized tests run over root/leaf, rack, datacenter/rack, datacenter/rack/nodegroup, and region/datacenter/rack/nodegroup schemas. Nodes are added to a fresh cluster, then tests query or mutate the topology. Selection tests run repeated random or sequential picks and assert excluded scopes, excluded nodes, ancestor generation, and affinity constraints.

## State And Persistence

State is in-memory topology tree state inside `NetworkTopologyImpl` and the singleton `NodeSchemaManager`, which each test reinitializes. There is no persistent store, but topology paths encode operational placement state.

## Dependencies And Integration Points

The suite integrates with `NodeSchema`, `NetConstants`, `NetUtils`, schema files under `networkTopologyTestFiles`, Mockito shuffle injection, JUnit parameterization, and SCM network placement logic.

## Risks

Randomized selection tests may be probabilistic, though repeated sequential helpers reduce missed coverage. The singleton schema manager can leak state if tests are reordered or parallelized unsafely. Exact exception message prefixes and distance-cost values are compatibility guards.

## Test Signals

Signals include correct leaf/node counts, invalid-depth rejection, config-file initialization, ancestor logic, inner-node mutation rejection, scoped and inverted-scope selection, exclusion enforcement, affinity confinement, single-node null selection, update semantics, cost calculations, distance sorting, and null-reader shuffle-only behavior.
