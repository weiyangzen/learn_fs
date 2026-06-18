# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/SecurityDescriptor.java

Source read signal: reviewed complete local file (252 lines, 6495 bytes).

## Purpose
`SecurityDescriptor.java` covers self-relative security descriptor serializer. represents owner/group SIDs, SACL, DACL, and control flags; writes SMB-required self-relative descriptors and reads offset-based descriptors.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Write emits header, reserves four offsets, serializes present owner/group/SACL/DACL, then backfills offsets and `SR`/present bits. Read saves start position, reads offsets, seeks to each present component, and constructs a descriptor.

## State and persistence
State is descriptor fields and control set; write mutates a local copy of controls, not the object.

## Dependencies and integration points
Integrates with ACL, SID, ACE, and SMB security-info operations.

## Risks
`EnumSet.copyOf(control)` fails for null or empty non-EnumSet inputs. Read does not restore buffer position to descriptor end after seeking through components.

## Test signals
Signals are descriptor roundtrip tests and SMB set/get security integration.
