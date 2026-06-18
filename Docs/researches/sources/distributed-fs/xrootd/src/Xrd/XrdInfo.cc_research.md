<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInfo.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdInfo.cc

Purpose: embeds the project license text into the `XrdLicense` string used by command-line help/license output.

Important APIs/types/functions: global `const char *XrdLicense`, initialized by including `../../LICENSE` as a string literal.

Control flow: no functions. The compiler expands the license file into a C string at build time.

State and persistence behavior: static read-only process data. It persists for the lifetime of the binary and is printed by `XrdConfig::Usage(-1)`.

Dependencies: includes `Xrd/XrdInfo.hh` and the relative `../../LICENSE` file, which must be formatted as includable string-literal content.

Integration points: `XrdConfig.cc` declares `extern const char *XrdLicense` and prints it for the `-H` option.

Risks: build breaks if the relative license path changes or the file is not valid for textual inclusion. License output can become stale if build packaging substitutes a different license without updating this include path.

Test signals: build test ensuring `XrdInfo.cc` compiles; CLI `xrootd -H` smoke test; packaging tests checking license file availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInfo.cc -->
