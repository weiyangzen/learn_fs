# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/NtlmConfig.java

## Purpose
Holds NTLM client configuration such as Windows version, workstation name, MIC/integrity preference, version omission behavior, and the 32-byte machine id used by single-host AV pairs.

## Important APIs / Types / Functions
Defines class `NtlmConfig` in package `com.hierynomus.ntlm`. Important methods/functions include `defaultConfig`, `builder`, `NtlmConfig`, `getWindowsVersion`, `getWorkstationName`, `isIntegrityEnabled`, `isOmitVersion`, `getMachineID`, `Builder`, `withWindowsVersion`, `withWorkstationName`, `withIntegrity`. Important fields include `windowsVersion`, `workstationName`, `integrity`, `omitVersion`, `machineID`, `config`. Source size: 128 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: windowsVersion, workstationName, integrity, omitVersion, machineID, config. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.messages.WindowsVersion, com.hierynomus.ntlm.messages.WindowsVersion.NtlmRevisionCurrent, com.hierynomus.ntlm.messages.WindowsVersion.ProductMajorVersion, com.hierynomus.ntlm.messages.WindowsVersion.ProductMinorVersion. JDK/JCE dependencies: java.security.SecureRandom, java.util.Random.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction; authentication behavior depends on nonce/machine-id randomness and should use SecureRandom in production.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
