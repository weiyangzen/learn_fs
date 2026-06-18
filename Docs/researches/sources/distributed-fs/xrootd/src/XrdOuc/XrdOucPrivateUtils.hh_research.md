<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPrivateUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPrivateUtils.hh

Purpose: Declares private utility helpers for path checks and sensitive CGI/header sanitization.

APIs and control flow: Inline `is_subdirectory()` checks whether `subdir` starts with `dir` and either ends there, continues with `/`, or `dir` itself ends with `/`. `obfuscateAuth()` hides authorization-like values. `stripCgi()` overloads remove selected CGI keys from `std::string` and `XrdOucString`. `splitHostCgi()` separates a `host[?cgi]` target into host and CGI portions.

State and persistence: Stateless utility declarations; functions mutate only caller-provided URL/string outputs.

Dependencies and integration: Includes `XrdOucString`, STL strings, regex, unordered sets, and string views. Implementations live in `XrdOucUtils.cc`.

Risks and test signals: Security-sensitive sanitization must handle case variants and malformed URLs. Tests should cover auth obfuscation variants, CGI key removal at beginning/middle/end, empty directories in `is_subdirectory()`, trailing slashes, and targets without `?`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPrivateUtils.hh -->
