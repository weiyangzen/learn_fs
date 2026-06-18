# File Research: sources/os/plan9/9front/sys/src/cmd/screenlock.c

Purpose: Locks a Plan 9 terminal by covering the display, grabbing input focus/mouse, blanking after inactivity, and requiring user authentication to unlock.

Key routines:
- `readline`: raw password input with delete/backspace/control-U handling and inactivity timestamp updates.
- `checkpassword`: loops until `auth_userpasswd(getuser(), password)` succeeds or key acquisition is needed.
- `blanker`: writes `blank` to `/dev/mousectl` after 5 seconds of no input.
- `grabmouse`: keeps the pointer centered by writing mouse reposition commands.
- `top`: watches `/dev/wctl` and makes the lock window current.
- `lockscreen`: opens a full-screen window, switches console to raw, draws `/lib/bunny.bit` and user/time text, starts helper procs, and clears cursor.
- `threadmain`: parses `-d`, locks, authenticates, exits all threads.

Integration: Uses Plan 9 draw/thread/auth/newwindow devices and `/dev/cons`, `/dev/mouse`, `/dev/wctl`.

Risks:
- Security depends on maintaining current window and mouse grab behavior.
- Password buffer is zeroed after use, but `AuthInfo` handling breaks out on `needkey`.
- Debug mode disables mouse recentering.
