# sources/user-network-fs/samba/source3/lib/smbd_shim.h

## Purpose
This header defines the `struct smbd_shim` callback table and declares the installer used by smbd to provide daemon-specific behavior to shared library code.

## Important APIs, Types, And Functions
`struct smbd_shim` contains callbacks for root-user changes, authenticated pipe user impersonation, level2 oplock contention begin/end hooks, root privilege enter/leave, and clean/unclean server exit. `set_smbd_shim()` installs the table. Function pointer signatures reference `auth_session_info`, `files_struct`, and `enum level2_contention_type`.

## Control Flow
The header has no executable logic, but it defines which operations can be dynamically dispatched by `smbd_shim.c`.

## State And Persistence
No state is declared here. The implementation stores a process-global copy of the table.

## Dependencies And Integration Points
The header expects surrounding Samba includes to provide bool, auth, file, and noreturn annotations. It is included by library code and smbd setup code to avoid hard dependencies on smbd internals.

## Risks And Test Signals
Risks are callback signature drift, missing declarations for the wrapper functions in this header, and caller confusion over default behavior. Build coverage across smbd and utility binaries is the main signal, with runtime tests in `smbd_shim.c`.
