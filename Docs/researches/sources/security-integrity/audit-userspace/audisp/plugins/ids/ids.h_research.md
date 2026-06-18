## sources/security-integrity/audit-userspace/audisp/plugins/ids/ids.h

Purpose: shared IDS globals and service APIs.

It defines daemon session/unset constants, exposes debug logging, audit event logging, HUP/state-dump flags, and reload/output functions. State is defined in `ids.c` and consumed by model/reaction modules. Dependencies are libaudit event type constants. Risks include global mutable flags shared across modules and no encapsulation of debug/mode behavior. Test signals are module behavior under reload and state dump.
