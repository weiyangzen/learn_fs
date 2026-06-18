# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMDatanodeProtocolServer.java

## Purpose

`TestSCMDatanodeProtocolServer` is a focused unit/integration test for command metadata returned by SCM's datanode protocol server. It verifies commands carry SCM term and deadline information.

## Important APIs, Types, And Functions

The single test `ensureTermAndDeadlineOnCommands` uses `SCMDatanodeProtocolServer`, SCM command builders, and command protobuf fields to ensure generated commands contain the expected term/deadline values.

## Control Flow

The test constructs or invokes command generation, then asserts the command metadata fields are populated. It does not need a full MiniOzoneCluster.

## State And Persistence Behavior

No durable state is changed. The validated state is transient command metadata used by datanodes to evaluate command freshness and leadership context.

## Dependencies And Integration Points

It integrates with SCM datanode protocol command construction and the datanode command-consumption contract.

## Risks And Test Signals

Missing term/deadline values can cause datanodes to execute stale commands or reject valid ones after leadership changes. Test failure is a direct signal that command metadata initialization changed.
