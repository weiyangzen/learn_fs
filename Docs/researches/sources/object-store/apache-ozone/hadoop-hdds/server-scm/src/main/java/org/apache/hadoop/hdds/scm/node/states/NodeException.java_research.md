# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeException.java

## Purpose
`NodeException` is the checked base class for node-state-map errors.

## Important APIs, Types, And Functions
It extends `Exception` and provides no-argument and message constructors.

## Control Flow
Subclasses such as `NodeAlreadyExistsException` and `NodeNotFoundException` are thrown by node state map operations and propagated through `NodeManager` APIs.

## State And Persistence Behavior
The class carries only exception message/cause state inherited from `Exception`. It has no persistence.

## Dependencies And Integration Points
It defines the common exception hierarchy for `org.apache.hadoop.hdds.scm.node.states`.

## Risks And Edge Cases
There is no cause-taking constructor, so wrapping lower-level exceptions would lose direct causal chains unless subclasses are extended.

## Test Signals
Direct tests are low value. API tests should assert callers handle the concrete checked subclasses.
