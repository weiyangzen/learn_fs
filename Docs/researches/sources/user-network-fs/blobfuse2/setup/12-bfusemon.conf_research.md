<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/12-bfusemon.conf -->
# sources/user-network-fs/blobfuse2/setup/12-bfusemon.conf

## Purpose
rsyslog filter for the Blobfuse2 monitor process `bfusemon`.

## Important APIs, Types, and Functions
The rule matches program name `bfusemon`, writes all messages to `/var/log/bfusemon.log`, and stops further processing.

## Control Flow and State
Declarative rsyslog config; state is the monitor log file.

## Dependencies and Integration Points
Installed under `/etc/rsyslog.d/`. Pairs with health monitor logging and logrotate configuration.

## Risks and Edge Cases
The stop directive prevents duplicate routing to generic logs, which may or may not be desired operationally. The rule depends on the program name being exactly `bfusemon`.

## Test Signals
Generate bfusemon logs and confirm they appear in `/var/log/bfusemon.log` after rsyslog reload.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/12-bfusemon.conf -->
