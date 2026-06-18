<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/message.c -->
# sources/security-integrity/audit-userspace/common/message.c

Purpose: centralized internal logging helper for audit userspace libraries and daemons.

Important APIs and functions: `_set_aumessage_mode` configures destination and debug enablement; `audit_msg` sends formatted messages to syslog or stderr unless quiet, suppressing debug messages unless enabled.

Control flow and state: two static globals hold current mode and debug policy. `audit_msg` saves and restores `errno` around logging, preserving caller error context.

Dependencies and integration: uses syslog priorities, stdarg formatting, `common.h`, and private declaration in `private.h`. `common.c` runlevel failures call into it.

Risks and test signals: global mode is process-wide and not synchronized, so concurrent reconfiguration is unsafe. Quiet default can hide diagnostics if callers forget configuration. Tests are indirect through components that assert log side effects or preserve errno.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/message.c -->
