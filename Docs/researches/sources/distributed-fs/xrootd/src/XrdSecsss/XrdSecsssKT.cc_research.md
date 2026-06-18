# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssKT.cc

Purpose: keytab storage, parsing, refresh, random key generation, lookup, and atomic rewrite support for SSS shared-secret keys.

Important APIs and functions: constructor/destructor, `addKey()`, `delKey()`, `getKey()`, `genFN()`, `genKey()`, `Refresh()`, `Rewrite()`, `getKeyTab()`, `fileMode()`, `isKey()`, `keyB2X()`, `keyX2B()`, and `ktDecode0()`. `XrdSecsssKTRefresh()` is the refresh-thread entry point.

Control flow: construction opens random source, stats and parses the keytab, then starts a refresh thread for client/server modes. `getKeyTab()` checks permissions, reads records, decodes tagged fields, discards expired non-admin keys, and orders entries. `getKey()` selects by name, key ID, or both, preferring unexpired keys for clients. `Rewrite()` creates parent paths, writes a temporary file, prunes expired/old keys, and renames atomically.

State and persistence: persistent state is the keytab file, defaulting to `$HOME/.xrd/sss.keytab`. In-memory state is a linked list of `ktEnt`, file mtime, mode, refresh interval, highest key ID, mutex, refresh thread, and static random fd.

Dependencies and integration: used by the SSS protocol and `xrdsssadmin`. Depends on `XrdOucStream`, `XrdOucUtils`, `XrdSysThread`, POSIX file APIs, and `/dev/urandom` or fallback pseudo-random generation.

Risks: security depends on strict file modes; `.grp` files intentionally allow group read. Fallback random generation is weaker. Refresh thread runs forever until destructor kills it. Text parser must reject malformed tags and overlong fields. `Refresh()` contains a suspicious expression `if ((retc == eInfo.getErrInfo()) == 0)`.

Test signals: parse valid/invalid keytabs, permissions rejection, `.grp` mode allowance, expired key pruning, name/key-ID lookup, refresh after mtime change, rewrite atomicity and keep count, random key length, and admin stdin mode.
