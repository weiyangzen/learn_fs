<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcConfiguration.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcConfiguration.cc

## Purpose

`XrdPfcConfiguration.cc` implements configuration parsing and startup validation for the proxy file cache plugin. It defines defaults, parses `pfc.*` directives, loads OSS/decision/purge plugins, checks filesystem spaces and xattr support, derives watermarks from capacity, and publishes effective settings to the environment and logs.

## Important APIs, Types, And Functions

- `XrdVERSIONINFO(XrdOucGetCache, XrdPfc)` exposes plugin version metadata.
- `Configuration::Configuration()` sets default cache policy values.
- `cfg2bytes()`, `blocksize_str2value()`, and `prefetch_str2value()` convert config strings.
- Directive parsers include `xcschk()`, `xdlib()`, `xplib()`, `xtrace()`, and `ConfigParameters()`.
- `test_oss_basics_and_features()` probes data/meta spaces by creating, opening, writing, xattr-setting, xattr-reading, and unlinking test files.
- `Cache::Config()` orchestrates full parsing, OSS loading, capacity validation, derived settings, resource monitor creation, and g-stream lookup.

## Control Flow

`Config()` opens the config file, creates an `XrdOucStream`, captures `pfc` directives, and uses `XrdOfsConfigPI` to parse/load the OSS plugin. It loops through `pfc.*` directives: known plugin/trace/checksum directives use dedicated parsers, while most tunables go through `ConfigParameters()`. After parsing, it sets `oss.runmode=pfc`, optionally inserts `libXrdOssCsi.so` for cache checksum checking, loads the OSS, restores run mode, probes spaces, computes watermarks using `StatVS`, parses flush and RAM defaults, logs the effective config, exports `XRDPFC.SEGSIZE`, enables prefetch when configured, records the g-stream pointer, and initializes `ResourceMonitor`.

## State And Persistence

The function mutates `m_configuration`, `m_trace->What`, `m_decisionpoints`, `m_purge_pin`, `m_oss`, xattr feature flags, `m_prefetch_enabled`, `Info::s_maxNumAccess`, `m_gstream`, and `m_res_mon`. It exports environment values `XRDPFC` and `XRDPFC.SEGSIZE`, sets `psx.CSNet`, and creates/removes probe files in configured OSS spaces.

## Dependencies And Integration Points

It integrates with `XrdOfsConfigPI`, `XrdOucStream`, `XrdOucPinLoader`, `XrdOuca2x`, `XrdOucUtils`, `XrdOss`, `XrdSysXAttr`, `XrdPfcInfo`, `XrdPfcResourceMonitor`, and purge/decision plugin symbols. It is called by `XrdOucGetCache()` before worker threads start.

## Risks And Edge Cases

- `xdlib()` and `xplib()` ignore a false return from plugin `ConfigDecision()`/`ConfigPurgePin()`.
- `test_oss_basics_and_features()` has early returns that can leak opened `XrdOssDF` objects on some failure branches.
- Some config errors log without returning false, for example unknown subdirectives in parts of `diskusage` or `onlyifcached`.
- `pfc.hdfsmode` returns false as unsupported after unreachable assignment code.
- `pfc.httpcc` calls `strcmp(val, ...)` without checking a missing value.
- Directory stats parsing prints to stdout in addition to logging.

## Test Signals

Tests should cover default config, client-mode defaults, every directive, bad units and bounds, disk/file watermark ordering, separate data/meta spaces, OSS load failure, xattr supported/unsupported probes, checksum/TLS environment export, decision and purge plugin load/config failure, effective log content, HTTP cache-control toggles, qfsredir toggles, and malformed missing-argument cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcConfiguration.cc -->
