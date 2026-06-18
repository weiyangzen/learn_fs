# File Research: sources/os/plan9/plan9/sys/src/cmd/screenlock.c

Plan 9 terminal screen locker.

Key behavior:
- Reads the current user from `#c/user`.
- Opens `/dev/vgactl` or `#v/vgactl` to blank/unblank the display.
- Creates a covering window based on `/dev/screen`, initializes draw, paints `/lib/bunny.bit`, and shows the current user/time.
- Opens `/dev/mouse` and continuously recenters the pointer to prevent interaction.
- Reads password input from `/dev/cons` in raw mode via `/dev/consctl`.
- Authenticates with `auth_userpasswd(user, password)` and exits all threads on success.

Important details:
- `-d` disables mouse grabbing.
- A background blanker blanks after activity-triggered delay.
- Password buffer is zeroed after use.
- Cursor is hidden by writing a zeroed cursor image to `/dev/cursor`.

Filesystem relevance:
- Direct use of Plan 9 device files: `/dev/screen`, `/dev/mouse`, `/dev/cons`, `/dev/consctl`, `/dev/cursor`, `/dev/vgactl`, and `#c/user`.
