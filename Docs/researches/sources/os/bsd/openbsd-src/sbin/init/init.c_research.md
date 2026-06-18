# File Research: sources/os/bsd/openbsd-src/sbin/init/init.c

This is OpenBSD’s classic PID 1 implementation. It manages the system boot state machine, single-user shell, `/etc/rc`, multi-user getty sessions from `/etc/ttys`, signal-driven transitions, security level changes, and shutdown/reboot.

Key responsibilities:
- Validates it is root and PID 1, redirects stdio to `/dev/null`, opens syslog, creates an initial session, sets login to root, parses `-s` and `-f`, installs signal handlers, blocks unrelated signals, and starts the state machine in `main`.
- Defines states:
  - `single_user`
  - `runcom`
  - `read_ttys`
  - `multi_user`
  - `clean_ttys`
  - `catatonia`
  - `death`
  - `do_reboot`
  - `hard_death`
  - `nice_death`
- Provides logging helpers `stall`, `warning`, and async-safe-ish emergency logging through `emergency`.
- Handles kernel securelevel via `getsecuritylevel` and `setsecuritylevel`.
- Runs single-user mode in `f_single_user`, including console controlling-terminal setup, optional root password check under `SECURE`, optional alternate shell under `DEBUGSHELL`, shell exec fallback, and restart/transition behavior.
- Runs `/etc/rc autoboot` or `/etc/rc` in `f_runcom`; on success logs reboot and proceeds to `/etc/ttys`.
- Builds and manages session descriptors from tty entries:
  - `new_session`, `setupargv`, `construct_argv`, `free_session`
  - linked list for ordered sessions
  - RB tree keyed by process ID for child lookup
- Starts optional window systems and getty processes with resource classes in `start_window_system` and `start_getty`.
- Prevents getty thrashing with monotonic timestamp spacing and sleep backoff.
- Handles child exits in `collect_child`, clears utmp/wtmp/fbtab state, restarts gettys, or removes shutdown sessions.
- Handles SIGHUP/SIGINT/SIGTERM/SIGUSR1/SIGUSR2/SIGTSTP in `transition_handler` by setting requested state transitions.
- Enters multi-user mode in `f_multi_user`, raises securelevel to 1 if appropriate, starts all gettys, and waits/restarts children until a transition is requested.
- Re-reads `/etc/ttys` in `f_clean_ttys`, updating changed sessions, marking removed/off sessions for shutdown, and adding new sessions.
- Blocks new logins in `f_catatonia`.
- Performs shutdown flows:
  - `f_death` brings system to single-user by signaling processes.
  - `f_nice_death` runs `/etc/rc shutdown`, may request powerdown, escalates SIGHUP/SIGTERM/SIGKILL, and calls `reboot`.
  - `f_do_reboot` and `f_hard_death` set reboot/powerdown flags.

Important OS/filesystem interactions:
- Reads `/etc/ttys` through ttyent APIs.
- Executes `/etc/rc` and shell paths from `pathnames.h`/`paths.h`.
- Opens/revokes terminal devices under `/dev`.
- Updates login accounting through `logout`, `logwtmp`, `login_fbtab`, and `acct`.
- Uses `login_cap` resource classes: `daemon`, `default`.
- Calls `reboot`, `sysctl`, `kill(-1, ...)`, `waitpid`, `setsid`, `login_tty`, and secure password functions under `SECURE`.

Security and correctness notes:
- PID 1 ignores/stages signals carefully so execed children get normal dispositions.
- Secure single-user mode checks root password when console is not marked secure.
- Securelevel is lowered for single-user and raised for multi-user unless configured otherwise.
- Shutdown escalates signals with timed wait windows to avoid hanging forever on stubborn processes.
