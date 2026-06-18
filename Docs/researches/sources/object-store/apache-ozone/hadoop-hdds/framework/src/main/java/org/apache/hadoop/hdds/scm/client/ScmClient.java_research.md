# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/client/ScmClient.java

## Purpose

`ScmClient` is the broad administrative/client facade for SCM container, pipeline, datanode, balancer, safe-mode, HA, secret-key, upgrade, metrics, and maintenance operations.

## Important APIs, Types, and Functions

It declares container creation/read/list/delete/close APIs, replica queries, node queries and admin state changes, pipeline lifecycle, safe-mode controls, replication manager controls/reporting, container balancer start/stop/status, SCM roles and leadership transfer, secret-key rotation, deleted-block summary, datanode usage, SCM upgrade finalization, SCM decommission, metrics, reconcile, and container suppression.

## Control Flow

The interface has no implementation. Concrete clients translate these calls to SCM protocols and compose lower-level SCM block/container/security RPCs.

## State and Persistence Behavior

No interface state. Implementations mutate SCM metadata: containers, pipelines, datanode admin state, balancer config/status, secret keys, and upgrade metadata.

## Dependencies and Integration Points

It ties command-line/admin consumers to SCM subsystems: container manager, pipeline manager, replication manager, container balancer, HA/Ratis, upgrade finalization, and metrics.

## Risks and Test Signals

The interface is wide and mixes read, write, admin, and long-running operations, so compatibility and authorization are critical. Tests should cover method-to-RPC mapping, optional balancer parameters, failure reporting lists, pagination/count limits, and close/resource behavior.
