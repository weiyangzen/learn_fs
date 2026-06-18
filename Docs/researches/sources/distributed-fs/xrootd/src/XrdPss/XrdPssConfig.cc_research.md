# sources/distributed-fs/xrootd/src/XrdPss/XrdPssConfig.cc

## Purpose

`XrdPssConfig.cc` performs startup configuration for the XRootD proxy storage service. It parses `pss.*`, `oss.defaults`, and `all.export` directives, initializes POSIX client settings, origin/forwarding proxy state, cache/N2N settings, persona mapping, reproxy support, permit rules, and exported environment variables used by downstream xrootd client code.

## Important APIs, Types, And Functions

- Static `XrdPssSys` members store global proxy configuration: `ConfigFN`, `myHost`, `myName`, `XPList`, `Police`, `ManList`, `fileOrgn`, `protName`, `hdrData`, `Streams`, `Workers`, trace flags, DCA/reproxy/persona booleans.
- `XrdPssSys::Configure(cfn, envP)` is the top-level initializer. It creates an `XrdOucPsx`, sets default `XrdPosixConfig` options, calls `ConfigProc()`, validates origin state, configures identity mapping, finalizes the POSIX client config, allocates `XrdPosixXrootd`, sets session-id support, registers accepted protocols, and exports `XRDXROOTD_PROXY`, `XRDXROOTD_ORIGIN`, and `XRDXROOTD_PROXYURL`.
- `ConfigProc()` opens and scans the config file with `XrdOucStream`, captures relevant directives, dispatches through `ConfigXeq()`, and finalizes export defaults.
- `ConfigXeq()` maps directives to parser methods. Some are delegated to `XrdOucPsx` (`namelib`, `cache`, `cachelib`, `inetmode`, `setopt`, `trace`), while local handlers cover `config`, `dca`, `defaults`, `export`, `origin`, `permit`, `persona`, `hostarena`, `localroot`, and `reproxy`.
- `ConfigMapID()` builds an `XrdSecsssID` mapper and enables URL identity mapping when persona mode requires client ID propagation.
- Directive parsers include `xconf()`, `xdca()`, `xdef()`, `xexp()`, `xorig()`, `xperm()`, and `xpers()`.

## Control Flow

Startup begins by collecting environment and instance identity, exporting `XRDXROOTD_NOPOSC=1`, creating `psxConfig`, applying debug/IP/event-loop defaults, and parsing the config file. After parsing, `Configure()` rejects configurations without an origin unless running as a forwarding proxy, re-exports cache stream state from `envP`, initializes persona mapping if requested, handles local roots, disables LFN-to-PFN mapping in forwarding mode, advertises cache/reproxy features, opens the TPC reproxy directory if enabled, finalizes `XrdOucPsx`, and installs it into `XrdPosixConfig`.

Origin parsing is central. `xorig()` supports local filesystem origins, regular host/port origins, protocol URLs, and forwarding-proxy syntax beginning with `=`. Forwarding syntax can restrict allowed protocols via `XrdPssUtils::Vectorize()` and `valProt()`. URL origins normalize `xroot` to `root` protocol names where needed and use protocol-specific default ports when omitted.

## State And Persistence

This file mutates process-wide static state. Configuration does not persist to disk beyond exported environment variables and the open `rpFD` directory descriptor for reproxy metadata. `ManList`, `fileOrgn`, `hdrData`, protocol vectors, permit lists, and POSIX config environment survive for the process lifetime. Several strings are heap-allocated with `strdup()` and intentionally live for the plugin lifetime.

## Dependencies And Integration Points

The file depends on `XrdOucPsx`, `XrdPosixConfig`, `XrdPosixXrootd`, `XrdPosixXrootdPath`, `XrdOucExport`, `XrdNetSecurity`, `XrdNetUtils`, `XrdSecsssID`, `XrdPssUrlInfo`, and `XrdPssUtils`. It integrates with the larger proxy implementation through global variables in the `XrdProxy` namespace, `XrdPssSys` feature flags, exported environment consumed by the xrootd client, and security persona mapping used later by URL generation.

## Risks And Edge Cases

- Configuration is global and order-sensitive; repeated `origin` directives replace `ManList` or `fileOrgn`.
- `xdca()` appears to check `"off"` against the current token before reading the recheck value, so `dca recheck off` may not behave as the comment implies.
- The domain check in `xorig()` compares `protName` to both `"http://"` and `"https://"` with `&&`, which can never be true; only hostname-without-dot can set `DirlistDflt`.
- Memory ownership is manual and mostly process-lifetime; early error returns after partial allocation can leave state set.
- Persona mapping is explicitly rejected for caching proxies and strict forwarding proxies; configuration tests need to cover those failures because enforcement happens only at startup.
- `ConfigProc()` dispatches `oss.defaults` and `all.export` using `var+4`, relying on those strings aligning with local handler names.

## Test Signals

Useful tests should parse origin forms for local paths, `root://`, `xroot://`, `http://`, `https://`, forwarding-only `=`, forwarding protocol lists, omitted ports, service-name ports, malformed URLs, and trailing `+`. Persona tests should cover client/server, verify/noverify, strict/nonstrict, cache rejection, and forwarding rejection. Reproxy tests need TPC env presence and directory-open failure. Export/default tests should assert `XPList`, object ID enablement, and the exported `XRDXROOTD_*` values.
