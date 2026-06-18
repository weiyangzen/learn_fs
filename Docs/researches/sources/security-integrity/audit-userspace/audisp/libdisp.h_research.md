## sources/security-integrity/audit-userspace/audisp/libdisp.h

Purpose: internal public interface for audit dispatcher integration with auditd.

It defines `event_t` as an audit dispatcher header plus maximum audit message buffer and declares dispatcher lifecycle, enqueue, reconfigure, child handling, queue state, and resume APIs. State is hidden in `audispd.c` and queue implementation. Dependencies are `libaudit.h` and `auditd-config.h`. Risks include fixed data buffer size and callers needing to respect header size/protocol fields. Test signals are auditd dispatcher integration and queue state output.
