# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/Replicate.java

## Purpose

`@Replicate` marks SCM metadata methods that should be invoked through Ratis rather than directly mutating local state.

## Important APIs, Types, and Functions

The annotation targets methods, is inherited, retained at runtime, and has `invocationType()` with enum values `DIRECT` and `CLIENT`, defaulting to `DIRECT`.

## Control Flow

Interceptors/proxies inspect the annotation at runtime. `DIRECT` submits to the local Ratis server and requires leadership; `CLIENT` submits through a Ratis client and need not run on the leader.

## State and Persistence Behavior

No state. It controls whether method effects are replicated and persisted through Ratis.

## Dependencies and Integration Points

Used by SCM HA metadata services/proxies that route annotated calls.

## Risks and Test Signals

Missing annotation on mutating methods can bypass replication; wrong invocation type can fail on followers or add unnecessary client hops. Tests should verify annotation discovery and routing for direct and client modes.
