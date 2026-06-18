# sources/security-integrity/selinux/restorecond/restorecond.desktop
# sources/security-integrity/selinux/restorecond/restorecond.desktop

Purpose: XDG autostart entry for user-mode restorecond.

Important content and control flow: declares a desktop application named "File Context maintainer" executing `/usr/sbin/restorecond -u`, with startup notification disabled and GNOME/systemd hints disabling or hiding it under systemd.

State and persistence: installed to `/etc/xdg/autostart`; controls session startup behavior.

Dependencies and integration points: integrates desktop sessions with user restorecond mode and systemd user service migration.

Risks and test signals: autostart may duplicate DBus/systemd activation if desktop/systemd handling changes. No direct tests.
