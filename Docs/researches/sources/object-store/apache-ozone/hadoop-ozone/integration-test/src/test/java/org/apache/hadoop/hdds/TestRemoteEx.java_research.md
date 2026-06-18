# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/TestRemoteEx.java

## Purpose

`TestRemoteEx` verifies that HDDS/SCM exception types survive Hadoop IPC `RemoteException` wrapping and unwrapping. It protects client-side error typing for exceptions returned across RPC boundaries.

## Important APIs, Types, And Functions

The class defines a local `SomeException extends SCMException` with a `ResultCodes.FAILED_TO_CHANGE_CONTAINER_STATE` code. `testSCMException()` uses Reflections to find every `SCMException` subtype under the package and passes each to `runUnwrappingRemoteException`. The helper builds a `RemoteException` from the exception class name and message, unwraps it through `unwrapRemoteException(clazz)`, and asserts the concrete class and message.

## Control Flow

The test discovers subclasses, then for each class executes a synthetic remote-wrap/unwrap round trip. There is no cluster startup.

## State And Persistence Behavior

No persistent state is touched. State is limited to reflection metadata and transient exception objects.

## Dependencies And Integration Points

It depends on `SCMException`, Hadoop's relocated `org.apache.hadoop.ipc_.RemoteException`, and `org.reflections.Reflections`. It integrates with the RPC exception contract expected by HDDS clients.

## Risks And Test Signals

New `SCMException` subclasses that lack suitable constructors or cannot be instantiated by Hadoop's unwrapping logic will fail here. This test is sensitive to package scanning and to exception class renames.
