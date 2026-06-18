# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairSingleHost.java

## Purpose
Typed AV pair for MsvAvSingleHost carrying custom data and the configured 32-byte machine id.

## Important APIs / Types / Functions
Defines class `AvPairSingleHost` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvPairSingleHost`, `read`, `write`. Important fields include `machineID`. Source size: 51 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
State fields observed: machineID. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Buffer.BufferException.

## Risks and Edge Cases
offset and cursor math should be fuzzed for malformed or truncated packets; mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
