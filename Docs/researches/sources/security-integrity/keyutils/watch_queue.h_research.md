<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/watch_queue.h -->
# sources/security-integrity/keyutils/watch_queue.h

## Purpose
Local copy of Linux watch queue UAPI definitions used by keyutils notification support.

## Important APIs, Types, And Functions
Defines `O_NOTIFICATION_PIPE`, watch queue ioctl numbers, `watch_notification_type`, metadata subtypes, `struct watch_notification`, filter structs, `struct watch_notification_removal`, key notification subtypes, and `struct key_notification`.

## Control Flow
This is a header-only ABI description. Runtime code includes it to format notification pipes, filters, and key notification records.

## State And Persistence Behavior
No state is held in the header. Its structures describe records delivered by kernel notification pipes.

## Dependencies And Integration Points
Includes `<linux/types.h>` and `<sys/ioctl.h>`. Integrates with keyutils watch/watch_session implementation and the test toolbox notification expectations.

## Risks And Edge Cases
Because this mirrors kernel UAPI, divergence from the running kernel can cause decode/filter mismatches. Bitfield layout and alignment are ABI-sensitive.

## Test Signals
Signals are successful compilation and correct interpretation of key notification types such as instantiated, updated, linked, unlinked, revoked, invalidated, and setattr.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/watch_queue.h -->
