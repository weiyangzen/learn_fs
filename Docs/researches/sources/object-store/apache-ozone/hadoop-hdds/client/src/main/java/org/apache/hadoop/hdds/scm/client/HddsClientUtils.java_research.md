# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/client/HddsClientUtils.java

Purpose: Shared utility methods for Ozone/HDDS clients, covering resource-name validation, retry-policy creation, config accessors, and exception unwrapping.

Important APIs/types/functions: `verifyResourceName` enforces S3-like bucket/volume/resource naming with optional non-strict underscore support. `verifyKeyName` validates key names with Ozone regex. `checkNotNull` validates varargs references. `getListCacheSize`, `getDefaultS3VolumeName`, and `getMaxOutstandingRequests` read client settings. `checkForException` unwraps nested exceptions against an expected list. `containsException` searches causal chains. `createRetryPolicy` and `getRetryPolicyByException` build Hadoop retry policies.

Control flow: Resource validation scans characters, detects all-numeric/IP-like names, checks unsupported characters and invalid dot/dash adjacency, then checks length and edge characters. Retry policy mapping uses zero-delay retries for timeout and Ratis retry failures and configured delay for other known exceptions.

State and persistence behavior: Static utility only. The exception list and log-name length constant are immutable static data.

Dependencies and integration points: Used by xceiver clients, stream output/input retry logic, and higher-level Ozone clients. Depends on Ozone constants, Ratis exceptions, Hadoop retry APIs, and HDDS configuration.

Risks: `verifyResourceName` loops over `resName.length()` before null checking, so null input causes `NullPointerException` rather than the intended `IllegalArgumentException`. `checkForException` returns the last cause if no expected class is found, which can affect retry-map lookups. Non-strict S3 behavior allows underscore only.

Test signals: Tests should cover invalid/valid resource names, null handling, long-name truncation in messages, IPv4/all-numeric rejection, key regex failures, retry policy mappings, and exception-chain search.
