# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CAType.java

## Purpose
Enumerates certificate authority types and their certificate filename prefixes.

## Important APIs and types
Values are `NONE("")`, `SUBORDINATE("CA-")`, and `ROOT("ROOTCA-")`. `getFileNamePrefix()` returns the prefix.

## Control flow and state
Enum state is immutable.

## Dependencies and integration points
Certificate authority and certificate lifecycle code can use it to name CA certificate files consistently.

## Risks and test signals
Tests should assert exact prefixes if file naming compatibility matters.
