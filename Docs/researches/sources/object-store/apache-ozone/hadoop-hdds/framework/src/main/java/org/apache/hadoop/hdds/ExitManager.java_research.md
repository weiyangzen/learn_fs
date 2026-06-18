<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/ExitManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/ExitManager.java

## Purpose
`ExitManager` wraps Ratis `ExitUtils.terminate` so services can be terminated on unrecoverable errors while tests can replace or intercept exit behavior.

## Important APIs, Types, and Functions
It exposes `exitSystem(int,String,Throwable,Logger)`, `exitSystem(int,String,Logger)`, `forceExit(int,Exception,Logger)`, and `forceExit(int,String,Logger)`.

## Control Flow
Each method delegates directly to the appropriate `ExitUtils.terminate` overload, deriving an exception message for `forceExit(int,Exception,Logger)`.

## State and Persistence Behavior
No state is owned. Effects are process termination or test-intercepted termination.

## Dependencies and Integration Points
It depends on `org.apache.ratis.util.ExitUtils` and SLF4J `Logger`, and integrates with HDDS service fatal-error paths.

## Risks and Test Signals
Risks include accidental real JVM termination in tests and losing exception detail through localized messages. Test signals are service fatal-error tests with mocked/replaced exit manager and Ratis ExitUtils interception.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/ExitManager.java -->
