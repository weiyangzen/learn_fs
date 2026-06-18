# sources/security-integrity/selinux/restorecond/restorecond_user.service
# sources/security-integrity/selinux/restorecond/restorecond_user.service

Purpose: systemd user unit for restorecond user mode.

Important content and control flow: requires `/etc/selinux/restorecond_user.conf` and SELinux, declares `Type=dbus`, bus name `org.selinux.Restorecond`, and `ExecStart=/usr/sbin/restorecond -u`.

State and persistence: systemd user instance and DBus activation manage lifecycle.

Dependencies and integration points: paired with `org.selinux.Restorecond.service` and user config.

Risks and test signals: service startup depends on DBus name acquisition in `user.c`; if DBus is unavailable, restorecond may use local lock fallback but systemd `Type=dbus` expects name ownership. No direct tests.
