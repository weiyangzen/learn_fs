# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsConfigPI.hh

## Purpose

This header defines the ABI-facing interface for OFS plugin configuration. It intentionally exposes methods but not implementation layout to callers, and requires callers to obtain instances through `XrdOfsConfigPI::New()`.

## Important APIs, types, and functions

`TheLib` encodes plugin families and their index bits: xattr, auth, checksum, CMS, FSctl, OSS, prepare, all, max count, and `libIXMask`. Public methods configure CMS/FSctl plugins, set defaults and checksum defaults, display settings, load requested plugin families, parse a directive, retrieve loaded plugin pointers, check checksum locality/OSS checksum use, check prepare authorization, push stackable plugins, and set checksum read size.

Private helpers mirror implementation responsibilities: `AddLib*()` for stacked plugins, `Parse*()` for directive-specific grammar, `RepLib()` for replacement, and `Setup*()` for primary plugin creation. The nested `xxxLP` owns copied library path, parameters, and option strings; `ctlLP` remembers FSctl plugin configure parameters.

## Control flow

Callers create an instance with `New()`, supply defaults before or after parse, call `Parse()` as each directive is encountered, then call `Load()` once with the requested bitmask. After load, `Plugin()` overloads provide typed plugin pointers to OFS. `ConfigCtl()` is intentionally separate because FSctl plugins receive the final authorization, CMS, OSS, and SFS plugin pointers.

## State and persistence behavior

The class stores plugin path strings, parameter strings, option strings, stacked plugin vectors, loaded raw pointers, version metadata, parser stream, logger, and flags such as `ossXAttr`, `ossCksio`, `prpAuth`, `Loaded`, `LoadOK`, and `cksLcl`. The state is process-local and not durable.

## Dependencies and integration points

The header includes `XrdCmsClient.hh` and forward-declares the major XRootD plugin interfaces. It integrates with OFS configuration, `XrdSfsFileSystem`, xattr setup, authorization, checksum management, CMS client generation, OSS storage, FSctl plugins, and prepare plugins.

## Risks and test signals

The enum values combine bit masks and indexes; any new plugin type must preserve `libIXMask` and `maxXXXLib` assumptions. `xxxLP::operator=` duplicates without freeing current members, which is acceptable for construction/vector copies but risky for true reassignment. Tests should pin ABI factory behavior, enum indexing, pushability rules, `Load()` idempotence, and pointer retrieval after successful and failed plugin loads.
