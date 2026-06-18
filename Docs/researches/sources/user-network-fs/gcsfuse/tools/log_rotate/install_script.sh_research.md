# sources/user-network-fs/gcsfuse/tools/log_rotate/install_script.sh

Purpose: installs hourly logrotate and rsyslog configuration for gcsfuse logs on Linux hosts.

Important APIs/types/functions: shell writes to `/etc/logrotate.hourly.conf`, `/etc/cron.hourly/gcsfuse-logrotate`, `/etc/logrotate.hourly.d/gcsfuse`, and `/etc/rsyslog.d/08-gcsfuse.conf`.

Control flow: creates hourly config directory, writes logrotate include config, writes an hourly cron script invoking `/usr/sbin/logrotate`, installs rotation policy for `/var/log/gcsfuse.log`, writes rsyslog filter for program name `gcsfuse`, then restarts rsyslog through `service` or `systemctl`.

State/persistence behavior: mutates system `/etc` configuration, cron hourly jobs, logrotate policy, rsyslog policy, and service state.

Dependencies/integration: requires root privileges and installed cron/logrotate/rsyslog tooling.

Risks/test signals: no `set -e`, so some earlier failures may not stop the script. It checks only the exit status of the immediately preceding `tee` or redirect blocks at a few points.
