# sources/sync-backup/syncthing/etc/linux-systemd/user/syncthing.service

## Purpose
This user-level systemd unit runs Syncthing inside a user's systemd session. It is simpler than the system-wide template and targets per-user autostart with moderate hardening.

## Important APIs, Types, And Functions
The unit defines `Description`, `Documentation`, `StartLimitIntervalSec=60`, `StartLimitBurst=4`, log-format environment variables, `ExecStart=/usr/bin/syncthing serve --no-browser --no-restart`, `Restart=on-failure`, `RestartSec=1`, `SuccessExitStatus=3 4`, `RestartForceExitStatus=3 4`, and hardening directives `SystemCallArchitectures=native`, `MemoryDenyWriteExecute=true`, and `NoNewPrivileges=true`. It installs into `WantedBy=default.target`.

## Control Flow
When enabled for a user, systemd starts Syncthing as part of the user's default target. Syncthing remains in foreground serve mode and delegates restart handling to systemd. Special exit statuses used for restart/upgrade are configured so systemd restarts rather than treating them as ordinary failures.

## State And Persistence Behavior
The process uses the invoking user's home directory and normal Syncthing state locations. Logs go to the user journal with formatting controlled by `STLOG...` environment variables. There is no pidfile or explicit state directory in the unit.

## Dependencies And Integration Points
It integrates with systemd user services, desktop/session startup, journald, and Syncthing's `serve` command. Compared with the system unit, it avoids `User=` because user managers already run as the target user.

## Risks And Edge Cases
User services require a working systemd user manager and may stop at logout unless lingering or desktop session behavior keeps them alive. The hardening is intentionally lighter than the system unit, so security posture differs between install modes. The hard-coded `/usr/bin/syncthing` path must match packaging. Optional ownership sync capabilities are commented as a hint but are generally more complex in user units.

## Test Signals
Validation should enable and start the unit with `systemctl --user`, inspect `journalctl --user-unit syncthing.service`, and confirm automatic restart on Syncthing restart exit codes. Desktop logout/login behavior should be tested according to distribution expectations.
