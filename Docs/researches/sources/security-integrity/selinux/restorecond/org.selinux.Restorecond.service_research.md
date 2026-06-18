# sources/security-integrity/selinux/restorecond/org.selinux.Restorecond.service
# sources/security-integrity/selinux/restorecond/org.selinux.Restorecond.service

Purpose: DBus service activation file for user restorecond.

Important APIs and control flow: declares service name `org.selinux.Restorecond`, executable `/usr/sbin/restorecond -u`, and associated systemd user service `restorecond_user.service`.

State and persistence: installed into the DBus services directory; DBus activation starts restorecond in user mode.

Dependencies and integration points: integrates session DBus with `restorecond_user.service` and `restorecond -u`.

Risks and test signals: incorrect path or service mismatch prevents activation. No direct test covers activation.
