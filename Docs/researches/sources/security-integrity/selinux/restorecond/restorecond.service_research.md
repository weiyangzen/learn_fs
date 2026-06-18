# sources/security-integrity/selinux/restorecond/restorecond.service
# sources/security-integrity/selinux/restorecond/restorecond.service

Purpose: systemd unit for root restorecond service.

Important content and control flow: starts after conditions `ConditionPathExists=/etc/selinux/restorecond.conf` and `ConditionSecurity=selinux`, runs `/usr/sbin/restorecond -F` as a simple foreground service, and installs into `multi-user.target`.

State and persistence: systemd manages process lifecycle; daemon relabels watched paths.

Dependencies and integration points: installed by the restorecond Makefile and paired with root config.

Risks and test signals: foreground mode avoids daemon double-fork under systemd. If config is missing or SELinux disabled, unit is skipped. No direct tests.
