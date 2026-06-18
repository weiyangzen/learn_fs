# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/NetworkTopologyImpl.java

## Purpose

`NetworkTopologyImpl` represents the cluster network tree and implements node membership, random placement selection, affinity/exclusion logic, distance costing, and replica sorting.

## Important APIs, Types, and Functions

Public APIs include `add`, `update`, `remove`, `contains`, ancestor/parent checks, `getNode(String)`, level counts/nodes, multiple `chooseRandom` overloads, indexed `getNode`, `getDistanceCost`, `sortByDistanceCost`, and `toString`. It uses a fair `ReentrantReadWriteLock` around mutable tree access.

## Control Flow

Construction initializes `NodeSchemaManager`, max level, root inner node, and shuffle operation. Add/update validate leaf depth against schema before mutating. Selection normalizes scope, handles reverse scopes, validates excluded scopes and affinity node, narrows scope to affinity ancestor when required, removes duplicate exclusions, computes available leaves, and chooses either a supplied index modulo availability or a random index. Distance cost climbs both nodes to a common ancestor, summing parent costs. Sorting groups nodes by cost and shuffles ties.

## State and Persistence Behavior

State is in-memory: schema manager, root `InnerNode`, max level, factory, shuffle function, and lock. Persistence/serialization of tree nodes is handled by `InnerNodeImpl` protobuf methods and SCM topology RPCs.

## Dependencies and Integration Points

It integrates with placement policies, OM topology cache, `NodeSchemaManager`, `NetUtils`, `InnerNodeImpl`, and datanode `Node` implementations.

## Risks and Test Signals

Several methods call other lock-taking methods while holding read locks; the lock is reentrant-compatible only because it is a `ReentrantReadWriteLock`. Selection mutates local exclusion collections and can return null for exhausted scopes. Tests should cover schema depth rejection, update replacing existing nodes, reverse scopes, affinity narrowing, ancestor-gen exclusions, distance sorting with shuffle tie behavior, and concurrent read/write access.
