# sources/distributed-fs/xrootd/src/XrdCks/XrdCksLoader.cc

Purpose: implements `XrdCksLoader`, the dynamic/native checksum calculator loader used by clients and by checksum manager autoload. It validates caller/plugin ABI compatibility with `XrdVersionInfo`, pre-registers native `adler32`, `crc32`, and `md5`, and builds the plugin path template `libXrdCksCalc%s.so`.

Important APIs: constructor/destructor, `Load()`, and private `Find()`. `Load()` is mutex-protected, returns either the original cached calculator or a fresh `New()` clone, lazily constructs native calculators, loads external calculators with `XrdOucPinLoader`, resolves `XrdCksCalcInit`, verifies the returned type name, and stores plugin handles in `csTab`.

Control flow and state: persistent process state is the in-memory `csTab[8]`, `csLast`, `ldPath`, `verMsg`, and pinned plugins. There is no disk persistence here. Dependencies are `XrdCksCalc*`, `XrdOucPinLoader`, `XrdSysPlugin`, and version macros. Risks include fixed table capacity, C string ownership, error-buffer truncation via `strncpy`, and strict plugin entry/type contracts. Test signals: native load, incompatible version, plugin missing symbol, wrong plugin type, table overflow, and concurrent first load.
