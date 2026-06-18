# File Research: sources/os/linux/linux-stable/fs/smb/client/dns_resolve.h

This header declares the CIFS DNS resolver helper API.

Main contents:
- Declares `dns_resolve_name(const char *dom, const char *name, size_t namelen, struct sockaddr *ip_addr)`.
- Provides `dns_resolve_unc()`, an inline helper that extracts the hostname portion from a UNC path and resolves it.

Important behavior:
- `dns_resolve_unc()` rejects missing or too-short UNC paths.
- It uses `extract_unc_hostname()` and returns `-EINVAL` if no hostname can be extracted.
- Resolution is delegated to `dns_resolve_name()` with optional DNS domain.

Research notes:
- This is the small public interface used by DFS and connection code to avoid duplicating UNC hostname extraction.
