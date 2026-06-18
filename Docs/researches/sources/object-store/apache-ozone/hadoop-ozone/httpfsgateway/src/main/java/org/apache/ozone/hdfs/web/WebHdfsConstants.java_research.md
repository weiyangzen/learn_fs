# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/hdfs/web/WebHdfsConstants.java

## Purpose
`WebHdfsConstants` centralizes WebHDFS and secure WebHDFS scheme/token identifiers used by the Ozone HttpFS gateway compatibility layer. It is a private utility class, not a runtime service.

## Important APIs, types, and functions
The class exposes `WEBHDFS_SCHEME`, `SWEBHDFS_SCHEME`, `WEBHDFS_TOKEN_KIND`, and `SWEBHDFS_TOKEN_KIND`. The token constants are Hadoop `Text` values matching WebHDFS delegation token kinds.

## Control flow
There is no control flow beyond class initialization of constants. A private constructor prevents instantiation.

## State and persistence behavior
The only state is immutable static constants. No configuration, filesystem, or durable state is read or written.

## Dependencies and integration points
The file depends on Hadoop `Text` and Ozone's private audience annotation. It integrates with code that needs canonical WebHDFS scheme names or token kind comparisons.

## Risks and edge cases
Changing string values would break protocol compatibility with WebHDFS clients or token consumers. The class intentionally mirrors Hadoop naming rather than deriving values dynamically.

## Test signals
There is no direct test in this subset. Coverage is indirect through HttpFS/WebHDFS authentication and client-compatibility paths.
