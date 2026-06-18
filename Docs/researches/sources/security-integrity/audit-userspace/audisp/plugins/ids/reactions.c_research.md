# sources/security-integrity/audit-userspace/audisp/plugins/ids/reactions.c

Purpose: executes IDS responses such as killing sessions, changing account state, blocking IPs, scheduling timed undo work, and changing runlevel.

Important APIs and data: implements process/session kill, SELinux role restriction, password reset, account lock/unlock, IP block/unblock, system reboot/single/halt, timed wrappers, and `do_reaction`. Local `safe_exec` forks and execs fixed tools with sanitized file descriptors.

Control flow: `do_reaction` iterates all 32 possible reaction bits and dispatches each set bit. Account reactions use `current_session()->acct`; address reactions use `current_origin()` and mark the origin blocked after firewall success. Timed account/address actions schedule jobs through timer services.

State and persistence: mutates external system state: processes, login/account database, SELinux login mapping, iptables/nftables rules, and runlevel. It also updates process-local origin blocked state and timer queue.

Dependencies and integration: depends on global `config`, current session/origin, `account.h`, timer services, audit response logging, syslog, password database, `/etc/login.defs`, and external binaries including `killall`, `semanage`, `chage`, `passwd`, `iptables`/`nft`, and `init`.

Risks: reactions are high-impact and many are irreversible or system-disruptive. `do_reaction` does not null-check current session before `kill_session(s->session)`. `verify_acct` rejects daemon/system accounts but depends on parsing UID_MIN. Firewall unblock must match the exact rule insertion form.

Test signals: unit tests should mock `safe_exec` and current session/origin; integration tests should isolate account/firewall side effects. Timed block/unblock paths are covered only through timer services behavior.
