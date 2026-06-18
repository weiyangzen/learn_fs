# sources/security-integrity/selinux/restorecond/restorecond_user.conf
# sources/security-integrity/selinux/restorecond/restorecond_user.conf

Purpose: user-mode restorecond watch list.

Important content and control flow: watches user-home patterns such as `~/*`, `~/public_html/*`, GNOME, local, fonts, cache, config, and local share directories. In user mode `~` expands to the current user's home; in root daemon mode `~` patterns are delegated through utmp watcher for logged-in users.

State and persistence: installed under `/etc/selinux/restorecond_user.conf`; changes reload watches.

Dependencies and integration points: consumed by `restorecond -u`, DBus service, and user systemd service.

Risks and test signals: broad home globs can cause many relabel operations and may miss deeply nested paths unless parent creates generate events. No direct tests.
