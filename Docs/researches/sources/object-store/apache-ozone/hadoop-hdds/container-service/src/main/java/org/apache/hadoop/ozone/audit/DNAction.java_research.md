# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/audit/DNAction.java

## Purpose
Enumeration of datanode audit action names for container, block, chunk, stream, checksum, and echo operations.

## Important APIs, Types, And Functions
Implements `AuditAction` and returns `toString()` from `getAction()`. Values include create/read/update/delete/list container, block and chunk operations, small file, stream init, finalize block, checksum info, and read block.

## Control Flow
Audit code can attach a typed enum value to audit records and serialize it through `getAction`.

## State And Persistence
No mutable state; enum constants are stable action identifiers.

## Dependencies And Integration Points
Integrates with Ozone audit framework and datanode command handlers.

## Risks
Renaming enum values changes audit output and can break downstream log analytics. Missing actions lead to generic or absent audit records.

## Test Signals
Signals include audit log records for each datanode operation and compatibility of action names with existing parsers.
