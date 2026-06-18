# sources/user-network-fs/samba/source3/include/local.h

## Purpose
`local.h` centralizes source3 server-side constants used by smbd, nmbd, winbindd, printing, locking, RPC, LDAP replication, and connection management. It is not an API implementation header; it fixes operational limits, default timeouts, database flags, string constants, and compatibility defaults that shape daemon behavior.

## Important APIs, Types, And Control Flow
The file defines no functions or structs. Important constants include open-file limits (`MIN_OPEN_FILES_WINDOWS`, `MAX_OPEN_FILES`, `MAX_OPEN_FUDGEFACTOR`), directory and pipe limits (`MAX_DIRECTORY_HANDLES`, `MAX_OPEN_PIPES`), password and list limits (`MAX_PASS_LEN`, `LIST_SEP`), browsing and NetBIOS timers, keepalive and connect timeouts, oplock break timeout/fudge, lock retry timing, auth mutex timing, share-name validation characters, volatile TDB hash size and flags, Windows minimum lock timeout, and `MAX_RPC_DATA_SIZE`.

## State And Persistence
The header does not store runtime state, but many constants govern persistent or shared state indirectly. `SERVER_LIST` names the browser database in the lock directory, TDB flags configure volatile databases used for open-file records, and timeout/limit constants affect how long entries, locks, name registrations, and failed connection cache data remain relevant.

## Dependencies And Integration Points
It integrates broadly through include chains that need source3 defaults before daemon initialization. Values here interact with loadparm settings such as `max open files`, TDB setup, NetBIOS browse services, RPC server limits, oplock handling, winbind cache sizing, and printer behavior.

## Risks And Test Signals
Risks are mostly compatibility and resource-boundary regressions: reducing file or pipe limits can break Windows clients, changing NetBIOS timers can destabilize browsing, altering volatile TDB flags can affect cleanup semantics, and enlarging RPC limits changes memory exposure. Test signals include smbd startup under low/high fd limits, Windows client file-open stress, RPC request size rejection, oplock break timing tests, NetBIOS browse registration timing, invalid share-name validation, and winbind cache behavior under multiple trusted domains.
