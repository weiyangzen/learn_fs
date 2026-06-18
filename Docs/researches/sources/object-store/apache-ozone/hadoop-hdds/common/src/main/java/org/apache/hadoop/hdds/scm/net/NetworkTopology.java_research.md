# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NetworkTopology.java

## Purpose
Defines the top-level interface for SCM network topology operations used by placement and node management.

## Important APIs, Types, And Functions
APIs include `add`, `update`, `remove`, `contains`, parent/ancestor comparisons, `getAncestor`, `getMaxLevel`, path lookup, leaf/node counts, node listing, random selection with scopes/exclusions/affinity, index-based selection, distance/cost calculation, and sort-by-distance. Nested `InvalidTopologyException` signals schema/topology errors.

## Control Flow
Implementations maintain topology state as datanodes enter/update/leave and serve placement queries that choose eligible nodes by scope, exclusion, and affinity.

## State And Persistence
Interface stores no state. Implementations are in-memory views derived from datanode registration and network schema.

## Dependencies And Integration Points
Works with `Node` and collections. Integrated by SCM placement policies, replication, and pipeline allocation.

## Risks And Test Signals
Scope syntax with `~`, affinity generation, and exclusion behavior are complex. Tests should cover random/index choice, invalid topology detection, distance sorting, update semantics, and concurrency in concrete implementations.
