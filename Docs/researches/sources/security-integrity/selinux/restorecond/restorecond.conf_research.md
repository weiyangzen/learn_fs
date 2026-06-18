# sources/security-integrity/selinux/restorecond/restorecond.conf
# sources/security-integrity/selinux/restorecond/restorecond.conf

Purpose: default root-mode restorecond watch list.

Important content and control flow: lists `/etc/services`, `/etc/resolv.conf`, Samba secrets, updatedb config, `/run/utmp`, `/var/log/wtmp`, `/root/*`, and `/root/.ssh/*`. `watch.c` reads each non-comment line and adds watches; wildcard patterns are expanded and watched at the parent-directory level.

State and persistence: installed under `/etc/selinux/restorecond.conf`; changes cause restorecond to reload because the config file itself is watched.

Dependencies and integration points: consumed by `restorecond.service` root daemon.

Risks and test signals: broad `/root/*` and `/root/.ssh/*` patterns cause relabeling of sensitive root files, which is intended but high impact if patterns are wrong. No tests cover config reload or specific paths.
