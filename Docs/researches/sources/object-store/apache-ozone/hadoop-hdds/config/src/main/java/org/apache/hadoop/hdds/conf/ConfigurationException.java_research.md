# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationException.java

## Purpose
Unchecked exception used for configuration injection, parsing, XML generation, and write-back failures.

## Important APIs, Types, And Functions
Provides no-arg, message, and message-plus-cause constructors.

## Control Flow
Callers wrap checked reflection, XML, parsing, or IO-related failures in this runtime exception to avoid polluting configuration APIs with checked exceptions.

## State And Persistence
No state beyond standard `RuntimeException` message and cause fields.

## Dependencies And Integration Points
Used throughout `org.apache.hadoop.hdds.conf`, especially reflection utilities and XML appender/generator code.

## Risks
Because it is unchecked, failures can surface at service startup or reconfiguration time unless callers validate config early. Some constructors allow empty messages, reducing diagnostic value.

## Test Signals
Signals include negative tests for malformed values, unsupported types, final annotated fields, bad XML resources, and post-construct rollback failures.
