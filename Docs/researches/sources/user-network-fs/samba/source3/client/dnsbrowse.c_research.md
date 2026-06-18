# sources/user-network-fs/samba/source3/client/dnsbrowse.c

## Purpose
`dnsbrowse.c` implements DNS-SD/mDNS browsing for SMB services when Samba is built with `WITH_DNSSD_SUPPORT`. It searches for `_smb._tcp` service instances, resolves them, and prints available host/port pairs. Without DNS-SD support it exposes a stub that reports the feature is unavailable.

## Important APIs, Types, And Functions
- `struct mdns_smbsrv_result` stores service name, registration type, domain, interface index, and a linked-list pointer.
- `struct mdns_browse_state` tracks the head of discovered services and whether browse callbacks have completed the current response batch.
- `do_smb_browse()` is the exported entry point.
- `do_smb_browse_reply()` is the `DNSServiceBrowse` callback, collecting add events into the talloc-backed linked list.
- `do_smb_resolve()` calls `DNSServiceResolve()` for each discovered service and waits for its socket to become readable.
- `do_smb_resolve_reply()` prints the resolved host target and port.

## Control Flow
`do_smb_browse()` opens a talloc stack frame, starts `DNSServiceBrowse()` for `_smb._tcp`, obtains the DNS-SD socket, and waits in a `poll_one_fd()` loop. When data arrives it calls `DNSServiceProcessResult()`, which invokes `do_smb_browse_reply()`. Added services are pushed to the result list. After browsing finishes or times out, the code deallocates the browse ref and iterates the result list, resolving each service instance with `do_smb_resolve()`. Resolution also waits on the DNS-SD socket and prints the first resolved endpoint.

## State And Persistence
State is transient and talloc-scoped to the browse call. The only persistent side effect is text output to stdout/stderr through `printf()`/`d_printf()`. No Samba databases or network connections are retained after `DNSServiceRefDeallocate()`.

## Dependencies And Integration Points
The implementation depends on Apple's/Avahi-compatible DNS-SD API (`dns_sd.h`), Samba `poll_one_fd()`, talloc stack frames, and smbclient command plumbing through `client_proto.h`. The fallback stub allows callers to compile regardless of platform DNS-SD availability.

## Risks
- The code contains unused variables and a `TALLOC_FREE(fdset)` call in `do_smb_resolve()` even though no `fdset` variable is declared in the visible source; this is a compile risk unless hidden by platform macros or stale code paths.
- `nextResult` is not explicitly initialized when the list is empty, so the last node may contain uninitialized memory unless talloc allocation happens to be zeroed elsewhere. It uses `talloc_array`, not `talloc_zero`.
- The loops use a fixed 1-second poll and stop after the first result batch, so browsing may miss late responders.
- Resolve errors are silently ignored after the initial error return.

## Test Signals
Build with and without `WITH_DNSSD_SUPPORT`; run under a DNS-SD responder advertising multiple SMB services; test no daemon, timeout, remove events, multiple interfaces, and malformed callback data. Static analysis should flag the `fdset` and uninitialized `nextResult` issues.
