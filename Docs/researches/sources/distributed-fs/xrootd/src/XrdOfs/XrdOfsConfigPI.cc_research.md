# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigPI.cc

## Purpose

This file implements `XrdOfsConfigPI`, the OFS plugin configuration and loading coordinator. It parses `ofs.*lib` directives, records default and explicit plugin paths/parameters, loads core and stacked plugins, wires plugin pointers into OFS, and preserves ABI compatibility by hiding class layout behind the factory method declared in the header.

## Important APIs, types, and functions

The constructor initializes all plugin pointers, the checksum configurator, version info, and pushability for each plugin family. `New()` performs version compatibility checking with `XrdSysPlugin::VerCmp` and returns an instance. `Parse()` dispatches directive parsing for xattr, auth, checksum, CMS, FSctl, OSS, and prepare plugins. Specialized parsers handle directive options: `ParseAtrLib()` supports `osslib` and `++`, `ParseOssLib()` supports `++`, `+cksio`, `+mmapio`, and `+xattr`, and `ParsePrpLib()` supports `++` and `+noauth`.

`Load()` is the central load sequence. It loads OSS first, then xattrs, auth, checksum, CMS, FSctl, and prepare plugins. `SetupAttr()`, `SetupAuth()`, `SetupCms()`, `SetupCtl()`, and `SetupPrp()` load primary plugins with `XrdOucPinLoader`; `AddLibAtr()`, `AddLibAut()`, `AddLibCtl()`, `AddLibOss()`, and `AddLibPrp()` layer additional `++` wrappers. `Default()`, `DefaultCS()`, `Push()`, `RepLib()`, and `SetCksRdSz()` set configuration before loading. The overloaded `Plugin()` methods return loaded plugin pointers.

## Control flow

Configuration starts by recording defaults or parsed directives into `LP[]` and `ALP[]`. `RepLib()` owns replacement semantics, parameter capture from `XrdOucStream::GetRest()`, and warnings when explicit directives override defaults. `Load()` is one-shot: subsequent calls return the cached `LoadOK`. OSS is loaded first because other plugins may depend on it, and the native OSS path can implicitly enable checksum I/O. Xattr loading either comes from OSS, an explicit xattr library, or the active default `XrdSysXAttrActive` plus optional wrappers.

Authorization loads the default object or a configured shared library and then applies auth wrappers. Checksum loading delegates to `XrdCksConfig`, optionally passing the OSS plugin for checksum I/O. CMS loading resolves `XrdCmsGetClient`. FSctl loading resolves `XrdOfsFSctl` and records stacked control plugins; `ConfigCtl()` later calls `Configure()` on the primary plugin and then the saved vector. Prepare loading resolves `XrdOfsgetPrepare` and wraps through `XrdOfsAddPrepare`.

## State and persistence behavior

State is in-memory plugin configuration: `LP[]` for primary libraries, `ALP[]` for stacked libraries, `ctlVec` for FSctl configure order, and loaded plugin pointers. `Loaded`/`LoadOK` cache the one-shot result. The file does not persist configuration, but it pins shared libraries and mutates process-global xattr behavior with `XrdSysFAttr::SetPlugin()`.

## Dependencies and integration points

This file depends on XRootD plugin/version infrastructure, `XrdOucStream`, `XrdOucPinLoader`, `XrdSysPlugin`, `XrdCksConfig`, `XrdSysFAttr`, `XrdAccAuthorize`, `XrdOss`, `XrdCmsClient`, `XrdOfsFSctl_PI`, and `XrdOfsPrepare`. It is the integration point between text configuration and runtime plugin objects used by OFS file operations, checksumming, CMS location, authorization, extended attributes, FSctl, and prepare handling.

## Risks and test signals

Plugin load order is critical; loading prepare before OSS or missing xattr routing would break downstream runtime calls. Stacked plugin ownership is mostly by pinned libraries and raw pointers, so lifetime and reconfiguration assumptions must be stable. `ConfigCtl()` configures `ctlPI` and then iterates `ctlVec`, which can include stacked plugins; tests should confirm FIFO/LIFO expectations. Parser tests should cover malformed options, `++` rejection for non-pushable libraries, default override warnings, path replacement after `PinLoader::Path()`, one-shot `Load()`, and version incompatibility in `New()`.
