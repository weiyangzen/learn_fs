# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_user.c

Core SMB user/session-logon object lifecycle. The file defines and implements user state transitions from logging on through logged on, logging off, logged off, and deferred deletion. It also owns credential privilege setup, admin detection, tree ownership accounting, netinfo encoding, and auth-logoff upcalls.

`smb_user_new` allocates a user from cache, assigns a UID from the session pool, creates an SMB2 session ID from the object address plus a low-bit generation counter, initializes state as `LOGGING_ON`, inserts into the session user list, increments server user counts, and cancels the session authentication timeout when the first user appears.

`smb_user_logon` transitions a logging-on user to logged-on, detaches auth socket/timeout, stores flags/domain/account/audit SID, duplicates strings, and calls `smb_user_setcred`. Blocking timeout cancellation and auth socket close happen outside the user mutex. `smb_user_logoff` handles logging-on and logged-on cases: it cancels pending auth resources, moves to `LOGGING_OFF`, disconnects owned trees for logged-on users, and notifies smbd of auth logoff unless the server is shutting down.

Reference management is state-aware. `smb_user_hold` only grants public holds for logged-on users, while `smb_user_hold_internal` is unconditional for internal ownership. `smb_user_release` flushes tree delete queues, decrements the refcount, and posts zero-ref logging-off users for deferred deletion. `smb_user_delete` removes the user from the session list, frees UID, schedules a session auth timeout if this was the last user and the session remains negotiated, synchronizes with the releasing mutex path, destroys credentials/strings/mutex, and frees the object.

Auth timeout handling uses `smb_user_auth_tmo` to allocate a synthetic request, take a user hold only if still logging on, and dispatch `smb_user_logoff_tq` to the worker taskq.

Credential setup maps SMB/Windows privileges to illumos privileges. Change-notify grants traverse bypass, take-ownership grants chown privileges, read/write file privileges grant DAC bypasses, and backup/restore create a privileged duplicate credential used for backup-intent access. `smb_user_has_security_priv` determines whether `ACCESS_SYSTEM_SECURITY` can be granted.

Other utilities include administrator SID/group detection, flexible user-name comparison (`name`, `domain\name`, `name@domain`), owned-tree count wait/broadcast support, user netinfo encoding for RPC, smbd auth-logoff door upcall throttling, and SID-based same-user comparison.
