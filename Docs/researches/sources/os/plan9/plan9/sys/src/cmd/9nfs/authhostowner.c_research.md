# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/authhostowner.c

Purpose: hostowner authentication proxy from remote 9P auth fid to local factotum.

Key behavior: decodes `AuthInfo`, drives `AuthRpc` with retry-on-key-needed behavior, proxies auth reads/writes over 9P `Tread`/`Twrite`, and attempts `Tauth` plus authenticated `Tattach` as local `getuser()`.

Integration notes: used by `srvinit`; if remote auth is not needed, `Tauth` failure path can be treated as success. Cleans temporary auth and attach fids by clunking through `xmesg`.
