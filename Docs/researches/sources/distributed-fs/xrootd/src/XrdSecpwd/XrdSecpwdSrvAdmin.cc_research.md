# sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecpwdSrvAdmin.cc

Purpose: standalone `xrdpwdadmin`-style administration program for XRootD password security files. It creates and mutates admin, user, netrc, and server-public-key files under `~/.xrd/` by default.

Important APIs and functions: `main()` parses options, opens an `XrdSutPFile`, handles actions, and writes `XrdSutPFEntry` records. `ParseArguments()`, `ParseCrypto()`, and `CheckOption()` drive global CLI state. `AddPassword()` has hashed and raw-password variants. `SavePasswd()`, `ReadPasswd()`, `SavePuk()`, `ReadPuk()`, `GeneratePuk()`, `ExpPuk()`, and `LocateFactoryIndex()` manage generated passwords and public-key cipher material.

Control flow: startup selects mode and file path, loads crypto factories, creates the backing file if requested, then dispatches `add`, `update`, `read`, `remove`, `disable`, `copy`, `trim`, or `browse`. Admin mode also ensures special entries for server ID, email, hostname, and cipher public keys. Password updates loop over crypto modules, create tags suffixed by crypto factory ID, and write one entry per module.

State and persistence: most program state is global. Persistent state is stored in `XrdSutPFile` records and side files under `genpwd/` and `genpuk/`. Password entries store salts and derived hashes unless `-nohash` is used for netrc compatibility. Public-key backup files serialize factory IDs, lengths, and cipher buckets.

Dependencies and integration: depends on `XrdSut` password-file primitives, `XrdCryptoFactory`, `XrdCryptoCipher`, `XrdOucString`, POSIX file APIs, user lookup, and directory scanning. Its outputs are consumed by the password security protocol and administrative deployment flows.

Risks: sensitive credentials can be written to generated password files by design, so permissions are critical. The code has many globals, manual memory ownership, interactive branches, and fixed-size parsing buffers. The default `PukFile` initializer contains a stale absolute path but is normally overwritten. Some write loops only retry `EINTR` and do not validate short writes.

Test signals: exercise all four modes with temporary `HOME`, verify file modes, add/update/remove/disable/copy/trim behavior, crypto-list handling, imported password/public-key parsing, one-time password state, public-key rotation preserving old buffers, and failure paths for missing factories or malformed import files.
