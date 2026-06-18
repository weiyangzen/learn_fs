# sources/sync-backup/syncthing/etc/linux-upstart/user/syncthing.conf

## Purpose
This Upstart user-session job starts Syncthing when a desktop session starts and stops it when the desktop session ends. It is intended for older desktop environments with Upstart user jobs.

## Important APIs, Types, And Functions
The job defines `env SYNCTHING_EXE="/usr/local/bin"`, `description`, `start on desktop-start`, `stop on desktop-end`, `env STNORESTART=yes`, `respawn`, and an `exec $SYNCTHING_EXE --no-browser` command. The comments describe the executable location and supervisor relationship.

## Control Flow
Upstart launches the job on the `desktop-start` event and stops it on `desktop-end`. `STNORESTART=yes` tells Syncthing not to manage its own restart loop, while `respawn` lets Upstart restart failed processes. Browser opening is disabled.

## State And Persistence Behavior
The job runs in the user's session context and uses that user's environment and default Syncthing locations. It persists no job-specific files. Logs are handled by Upstart/session logging.

## Dependencies And Integration Points
It depends on Upstart user-session events and a Syncthing executable configured by `SYNCTHING_EXE`. It is conceptually similar to the Linux desktop autostart file but uses Upstart supervision and respawn behavior.

## Risks And Edge Cases
The variable name/comment says executable location, but the default value is a directory and the `exec` line uses `$SYNCTHING_EXE --no-browser`, which appears inconsistent unless customized to a full binary path. The command also omits the modern `serve` subcommand. Upstart user sessions are legacy and distribution-specific, so events may not fire on modern desktops.

## Test Signals
Functional testing should occur on an Upstart desktop session: trigger desktop-start, confirm Syncthing runs without opening a browser, verify respawn, and confirm desktop-end stops the process. The executable variable should be customized and tested explicitly.
