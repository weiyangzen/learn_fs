# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/submodule/SMB2LockElement.java

## Purpose
Carries one SMB2 lock range and validates that the supplied lock flag set is one of the protocol-permitted combinations.

## Important APIs / Types / Functions
Defines class `SMB2LockElement` in package `com.hierynomus.mssmb2.messages.submodule`. Important methods/functions include `SMB2LockElement`, `getOffset`, `getLength`, `getLockFlags`, `toString`. Important fields include `VALID_FLAG_COMBINATIONS`, `offset`, `length`, `lockFlags`. Source size: 66 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: VALID_FLAG_COMBINATIONS, offset, length, lockFlags. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.mssmb2.SMB2LockFlag. JDK/JCE dependencies: java.util.Arrays, java.util.EnumSet, java.util.List, java.util.Set.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
