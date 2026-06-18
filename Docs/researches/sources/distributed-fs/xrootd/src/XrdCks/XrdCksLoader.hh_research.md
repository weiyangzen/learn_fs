# sources/distributed-fs/xrootd/src/XrdCks/XrdCksLoader.hh

Purpose: declares the checksum loader interface for obtaining `XrdCksCalc` implementations by algorithm name. The public contract states that native `adler32`, `crc32`, and `md5` are built in and up to five additional algorithms can be loaded from shared libraries.

Important APIs/types: `XrdCksLoader::Load(csName, csParms, eBuff, eBlen, orig)`, constructor with compile-time version info and optional library path, destructor, and private `csInfo` entries carrying `Name`, cached `Obj`, and pinned `Plugin`. `csMax` is 8 and `csTab` is an ordered fixed-size registry.

Control flow/state: the header establishes that callers normally receive a new calculator object whose `Recycle()` method owns destruction; `orig=true` is reserved for manager autoload. The first two members are explicitly version/error fields, suggesting plugin/version loader layout sensitivity. Dependencies are forward declarations for calculator/plugin/version types. Risks: fixed capacity, legacy raw pointers, and ownership split between `Recycle()`, `free()`, and `delete`. Test signals come from API-level construction/destruction, repeated loads, and plugin lifecycle validation.
