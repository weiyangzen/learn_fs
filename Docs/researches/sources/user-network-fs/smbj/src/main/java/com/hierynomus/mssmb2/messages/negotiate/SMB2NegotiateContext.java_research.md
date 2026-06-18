# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2NegotiateContext.java

## Purpose
Provides the common header, factory, read, and write mechanics for SMB2 negotiate contexts. Subclasses contribute the variable data body while this base class handles context type, data length, reserved bytes, and 8-byte alignment skip on reads.

## Important APIs / Types / Functions
Defines class `SMB2NegotiateContext` in package `com.hierynomus.mssmb2.messages.negotiate`. Important methods/functions include `SMB2NegotiateContext`, `write`, `writeContext`, `writeContextHeader`, `factory`, `read`, `readContext`, `readContextHeader`, `getNegotiateContextType`. Important fields include `negotiateContextType`. Source size: 114 lines.

## Control Flow
Control flow is serializer/parser oriented: write builds a temporary body, prefixes the context header, then appends body bytes; factory reads the context type and dispatches to the specific subclass; read consumes the data length, lets the subclass parse the body, then skips padding when more context bytes remain.

## State and Persistence
State fields observed: negotiateContextType. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.EnumWithValue, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.smb.SMBBuffer, com.hierynomus.smbj.common.SMBRuntimeException.

## Risks and Edge Cases
offset and cursor math should be fuzzed for malformed or truncated packets; unknown enum values must be handled deliberately to avoid null propagation or unexpected runtime failures; some API surface intentionally throws unsupported/TODO behavior and callers need explicit coverage.

## Test Signals
Round-trip SMB2 negotiate-context fixtures with counts, unknown ids, alignment padding, and empty-field validation.
