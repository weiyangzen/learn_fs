# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestFailoverWithSCMHA.java

## Purpose

`TestFailoverWithSCMHA` verifies client-visible behavior during SCM HA leader failover. It also checks that container balancer configuration persists across SCMs and that admin commands show retry guidance when SCM is unavailable.

## Important APIs, Types, And Functions

The test builds a MiniOzone HA cluster with one OM and three SCMs. It uses Ozone client key operations, SCM leader discovery, SCM shutdown/restart, container balancer configuration, and Ozone admin command execution. Constants define SCM/OM service IDs and SCM admin command families.

## Control Flow

Setup starts the HA cluster. `testFailover` performs writes, shuts down the active SCM, waits for a new leader, and verifies client operations continue. `testContainerBalancerPersistsConfigurationInAllSCMs` updates balancer config and verifies replication to all SCMs. `testRetryMessageShownWhenScmUnavailable` runs admin commands while SCMs are unavailable and checks user-facing retry output.

## State And Persistence Behavior

The tests persist OM keys, SCM HA Ratis state, balancer configuration, and leader/follower state. Failover validates that SCM metadata and service discovery survive leader replacement.

## Dependencies And Integration Points

It integrates MiniOzone HA, Ozone clients, SCM Ratis leader election, container balancer configuration storage, and admin CLI command handling.

## Risks And Test Signals

Failures indicate HA failover gaps, stale SCM client routing, missing replicated configuration, or poor unavailable-service messaging. Timing around leader election is the main flakiness vector.
