# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccConfig.cc

## Purpose

`XrdAccConfig.cc` implements default authorization system configuration. It parses `acc.*` directives, chooses an auth DB path, periodically refreshes the authorization database, converts DB records into access tables and capability chains, configures audit/group options, and publishes refreshed tables to `XrdAccAccess`. The file was read completely.

## Important APIs, Types, and Functions

The global `XrdAccConfiguration` is the singleton config object. `XrdAccConfig_Refresh()` runs periodic warm refresh. The constructor picks `/opt/xrd/etc/Authfile` or `/etc/xrootd/authdb` if readable and sets defaults. `Configure()` creates `XrdAccAccess`, parses config, loads DB, and starts the refresh thread. `ConfigDB()` creates fresh hashes, reads records, validates and swaps tables. `ConfigFile()` scans config directives. `ConfigXeq()` dispatches directives. Directive handlers include `xaud`, `xart`, `xdbp`, `xenc`, `xglt`, `xgrt`, `xnis`, and `xspc`. `ConfigDBrec()` builds capabilities for each auth DB record. `idDef()` and `idChk()` handle set selectors and inclusive/exclusive ordering. `PrivsConvert()` maps privilege characters to masks.

## Control Flow

Startup calls `Configure()`: parse config, load database cold, and start refresh. The refresh thread sleeps `AuthRT` seconds and calls `ConfigDB(1)`, which returns early if `Database->Changed()` says unchanged. DB records are streamed one at a time. Normal id records build capability chains from template references or path/privilege pairs. `=` records define named selector sets, `x` records create exclusive set rules, and `s` records create inclusive set rules. After successful parse, empty hashes are deleted, set lists are ordered, and `Authorization->SwapTabs()` publishes the new tables.

## State and Persistence Behavior

State includes auth DB provider, auth DB path, authorization object, group master, refresh interval, options, current rule number, space substitution char, URI-path decoding flag, config mutex, and refresh thread handle. Persistent state is external config/auth DB files; runtime state is rebuilt into memory on each successful refresh.

## Dependencies and Integration Points

It integrates with `XrdOucStream`, `XrdOucEnv`, `XrdOucUri`, `XrdOuca2x`, `XrdSysThread`, `XrdAccAccess`, `XrdAccAuthDB`, `XrdAccGroups`, `XrdAccAudit`, and `XrdAccCapability`.

## Risks and Edge Cases

`xdbp()` overwrites `dbpath` without freeing an existing value, leaking on repeated config parsing. Refresh thread runs forever and uses the `XrdSysError` pointer passed at startup. Duplicate rules, missing templates, invalid privileges, or unused set definitions are handled through diagnostics and failed refresh. `PrivsConvert()` supports negative privilege transition only once. URI decoding uses stack allocation sized to encoded path length. Warm refresh skips reload if `Changed()` returns false after stat errors.

## Test Signals

Tests should cover all directives, default path selection, cold and warm DB loads, refresh skip/change detection, record types `g/h/n/o/r/t/u/x/=/s`, templates, duplicate detection, exclusive ordering, inclusive accumulation, URI path decoding, space substitution, negative privileges, and concurrent access during table swap.
