# File Research: sources/windows/reactos/drivers/filesystems/npfs/seinfo.c

## Purpose
Implements query/set security information for named-pipe FCB security descriptors.

## Main Responsibilities
- `NpCommonQuerySecurityInfo`:
  - Validates CCB handle.
  - Calls `SeQuerySecurityDescriptorInfo` against `Fcb->SecurityDescriptor`.
  - Converts `STATUS_BUFFER_TOO_SMALL` to `STATUS_BUFFER_OVERFLOW` and reports required length.
- `NpCommonSetSecurityInfo`:
  - Validates CCB handle.
  - Builds a modified descriptor with `SeSetSecurityDescriptorInfo`.
  - Logs/caches it with `ObLogSecurityDescriptor`.
  - Replaces `Fcb->SecurityDescriptor` and dereferences the old descriptor.
- `NpFsdQuerySecurityInfo` and `NpFsdSetSecurityInfo` wrap common helpers under exclusive VCB locking.

## Important Interactions
- Security descriptors are assigned for new pipes in `create.c`.
- Access checks for opens use the FCB security descriptor in `create.c`.

## Risks / Review Notes
- Query and set both take the exclusive VCB lock, which is conservative.
- Set path assumes `SeSetSecurityDescriptorInfo` returns a descriptor distinct from the old one, asserted in code.
