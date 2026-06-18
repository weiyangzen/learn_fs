<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixFile.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixFile.cc

Purpose: implements the runtime behavior of the XrdCl proxy-prefix file plugin. It wraps an `XrdCl::File`, rewrites the URL passed to `Open()` by prepending a proxy prefix, and delegates all later file operations to the wrapped file object.

Important APIs/types/functions: `ProxyPrefixFile::Open()` rejects double-open, creates `XrdCl::File(false)`, calls `ConstructFinalUrl()`, and opens the rewritten URL; `GetPrefixUrl()` reads `XROOT_PROXY` then `xroot_proxy`; `trim()` removes leading/trailing spaces from exclusion tokens; `GetExclDomains()` parses `XROOT_PROXY_EXCL_DOMAINS`; `ConstructFinalUrl()` applies suffix exclusion checks and prepends the prefix; `GetFqdn()` canonicalizes hostnames with `getaddrinfo()`.

Control flow: `Open()` is the only operation with plugin-specific behavior. URL construction reads environment, parses the original URL host with `XrdCl::URL`, strips any port, canonicalizes the host, checks comma-separated exclusion suffixes, and conditionally inserts the prefix at the start of the original URL.

State/persistence: `mIsOpen` and `pFile` are in-memory state. Configuration is read from environment variables every time a URL is constructed; no persistent files are written.

Dependencies/integration: depends on `XrdCl::File`, `XrdCl::URL`, `XrdCl::DefaultEnv` logging, POSIX environment variables, and DNS canonicalization through `getaddrinfo()`.

Risks/test signals: `trim()` dereferences iterators before checking empty strings, so empty exclusion tokens can be unsafe. The suffix exclusion guard compares exclusion length to `url_prefix.size()` instead of the origin host length, risking incorrect matches or reverse-iterator overrun when an exclusion is longer than the host. DNS canonicalization can block or fail, in which case the raw host is used. Tests should cover empty/missing prefix, uppercase/lowercase env names, exclusion suffixes, hosts with ports, unresolved hosts, double open, and URL rewrite logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixFile.cc -->
