# File Research: sources/os/bsd/netbsd-src/lib/libutil/login_cap.c

## Purpose
Implements login class capability lookup and user/session context setup.

## Key Details
- `login_getclass` validates `_PATH_LOGIN_CONF` with `secure_path`, then loads class capabilities with `cgetent`.
- Capability getters parse strings, booleans, numbers, times, and sizes:
  - `login_getcapstr`
  - `login_getcapbool`
  - `login_getcapnum`
  - `login_getcaptime`
  - `login_getcapsize`
- `setusercontext` applies resource limits, priority, umask, gid/groups, login name, uid, environment, and PATH according to flags.
- Creates per-user temporary directories when `/tmp` is a magic symlink ending in `/@ruid`.
- `setuserenv` parses login class `setenv`.
- `setuserpath` expands `~` entries in login class PATH using the user home directory.
- Internal size parsing supports suffixes `b`, `k`, `m`, `g`, `t` and multiplicative expressions, with overflow detection.

## Dependencies and Role
- Security-sensitive account/session setup code.
- Uses filesystem state for login config trust checks and per-user temp directory creation.
