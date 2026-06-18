# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssAdmin.cc

Purpose: command-line keytab administration utility `xrdsssadmin` for adding, deleting, installing, and listing SSS shared-secret keys.

Important APIs and functions: `main()` parses options into `XrdsecsssAdmin_Opts`. Actions dispatch to `XrdSecsssAdmin_addKey()`, `delKey()`, `insKey()`, and `lstKey()`. Helpers include `getXDate()`, `isNo()`, `Usage()`, `XrdSecsssAdmin_isKey()`, and `XrdSecsssAdmin_Here()` for filtering and sorting.

Control flow: options select key name/user/group, expiration, keep count, key length, key number, debug, and sort column. `add` creates or opens a keytab, appends a generated key, and rewrites. `del` filters by key attributes or number and may unlink the file if no keys remain. `install` reads keytab data from stdin and writes selected keys to a destination. `list` loads, sorts, filters, and prints table rows.

State and persistence: persistent state is the keytab file path, defaulting through `XrdSecsssKT::genFN()`. Rewrites prune expired keys and enforce the per-name keep count. Expiration accepts days-from-midnight or `%D` date format.

Dependencies and integration: built from `XrdSecsss/CMakeLists.txt`, linked with `XrdUtils`, and depends on `XrdSecsssKT`, POSIX file APIs, `XrdSysTimer`, and error translation.

Risks: destructive delete paths are interactive but still powerful. `install` depends on stdin parsing through the keytab class. Option `-h` is used for hold count rather than help. Expiration parsing through `strptime("%D")` is locale/time-zone sensitive.

Test signals: add/list/delete/install against temporary keytabs, check key length normalization to multiples of four, expiration pruning, sorting columns, nonexistent file behavior, all-keys-deleted prompt, and stdin install filtering.
