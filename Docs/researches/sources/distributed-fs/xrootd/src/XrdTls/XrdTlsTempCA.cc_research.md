# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsTempCA.cc

Purpose: Implements a temporary bundled CA/CRL file manager that scans a CA directory, deduplicates PEM CAs and CRLs, writes consolidated files under XRDADMINPATH/.xrdtls, and refreshes them periodically for consumers such as libcurl.

Important APIs/types/functions: Local Set wraps output FILE ownership. CASet::processFile() parses certificates into XrdCryptoX509Chain and writes unique subject hashes. CRLSet::processFile() parses CRLs, tracks unique issuer hashes, records whether any CRL was valid, and defers CRLs with critical extensions for processCRLWithCriticalExt(). TempCAGuard::create(), commit(), and destructor manage mkstemps-created files. XrdTlsTempCA constructor/destructor, Maintenance(), and MaintenanceThread() own lifecycle.

Control flow: Constructor creates two pipes, runs initial Maintenance(), then starts a refresh thread. Maintenance() requires XRDADMINPATH, creates temp CA/CRL files, opens the configured CA directory, iterates regular files/symlinks, processes each first as CA then as CRL, writes deferred critical-extension CRLs at the end, atomically renames temp files to ca_file.pem/crl_file.pem, and publishes shared_ptr filenames. MaintenanceThread() polls for shutdown or refresh interval, retrying sooner after failure.

State/persistence: Persistent outputs are ca_file.pem and crl_file.pem under XRDADMINPATH/.xrdtls. Runtime state includes pipe fds, m_ca_file/m_crl_file shared pointers, and m_atLeastOneCRLFound.

Dependencies/integration: Uses XrdSysFD wrappers, XrdSysError, XrdSysThread, XrdCrypto X509/CRL helpers, OpenSSL-backed parsing, filesystem dirent/stat APIs, and XrdVersion.

Risks: Destructor pipe loops appear to continue while rval != -1 || errno == EINTR, which deserves review because successful write/read may not break. Directory fd ownership on fdopendir failure may leak. Publishing shared_ptr filenames avoids locking but callers can observe old file paths until refresh completes. Output file permissions inherit mkstemps defaults/umask.

Test signals: Tests should cover missing XRDADMINPATH, unreadable CA dir, mixed CA/CRL/noncert files, duplicate hashes, CRLs with critical extensions, atomic file replacement, refresh after failure, shutdown thread exit, and IsValid/atLeastOneValidCRLFound.
