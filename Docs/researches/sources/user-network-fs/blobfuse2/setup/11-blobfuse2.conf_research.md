<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/11-blobfuse2.conf -->
# sources/user-network-fs/blobfuse2/setup/11-blobfuse2.conf

## Purpose
rsyslog filter that routes Blobfuse2 program logs into dedicated log files.

## Important APIs, Types, and Functions
The rule matches `:programname, isequal, "blobfuse2"`. It writes all messages to `/var/log/blobfuse2.log`, writes messages containing `"REQUEST"` to `/var/log/blobfuse2-rest.log`, then stops further processing.

## Control Flow and State
This is declarative rsyslog configuration. Runtime state is the log files managed by rsyslog and logrotate.

## Dependencies and Integration Points
Installed under `/etc/rsyslog.d/` and paired with `setup/blobfuse2-logrotate`. Integrates with syslog logging mode in Blobfuse2.

## Risks and Edge Cases
All Blobfuse2 logs are stopped after this rule, so downstream rsyslog rules will not receive them. The `"REQUEST"` substring filter can overmatch or undermatch REST traces.

## Test Signals
After rsyslog restart, Blobfuse2 syslog entries should appear in `/var/log/blobfuse2.log`; request traces should additionally appear in `/var/log/blobfuse2-rest.log`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/11-blobfuse2.conf -->
