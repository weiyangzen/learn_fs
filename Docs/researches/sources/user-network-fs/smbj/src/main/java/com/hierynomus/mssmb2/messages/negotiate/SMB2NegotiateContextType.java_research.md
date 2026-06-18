# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2NegotiateContextType.java

## Purpose
Enumerates SMB2 negotiate context type wire values used by the negotiate context factory and serializers.

## Important APIs / Types / Functions
Defines enum `SMB2NegotiateContextType` in package `com.hierynomus.mssmb2.messages.negotiate`. Important methods/functions include `SMB2NegotiateContextType`, `getValue`. Important fields include `value`. Source size: 38 lines.

## Control Flow
Control flow is serializer/parser oriented: write builds a temporary body, prefixes the context header, then appends body bytes; factory reads the context type and dispatches to the specific subclass; read consumes the data length, lets the subclass parse the body, then skips padding when more context bytes remain.

## State and Persistence
State fields observed: value. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.EnumWithValue.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Round-trip SMB2 negotiate-context fixtures with counts, unknown ids, alignment padding, and empty-field validation.
