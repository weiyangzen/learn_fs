# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/WindowsVersion.java

## Purpose
Represents the NTLM VERSION structure and nested enums for product major, minor, build, and revision values.

## Important APIs / Types / Functions
Defines class `WindowsVersion` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `ProductMajorVersion`, `getValue`, `ProductMinorVersion`, `NtlmRevisionCurrent`, `WindowsVersion`, `readFrom`, `writeTo`, `toString`, `equals`, `hashCode`, `getNtlmRevision`. Important fields include `value`, `value`, `value`, `majorVersion`, `minorVersion`, `productBuild`, `ntlmRevision`. Source size: 130 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: value, value, value, majorVersion, minorVersion, productBuild, ntlmRevision. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.EnumWithValue, com.hierynomus.protocol.commons.buffer.Buffer. JDK/JCE dependencies: java.util.Objects.

## Risks and Edge Cases
offset and cursor math should be fuzzed for malformed or truncated packets; unknown enum values must be handled deliberately to avoid null propagation or unexpected runtime failures; mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
