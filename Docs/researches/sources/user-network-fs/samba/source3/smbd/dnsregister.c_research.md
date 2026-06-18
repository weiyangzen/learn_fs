# sources/user-network-fs/samba/source3/smbd/dnsregister.c

## Purpose
`dnsregister.c` optionally registers smbd as an `_smb._tcp` service through DNS Service Discovery/mDNS. Without DNSSD support it exposes a successful no-op setup function.

## Important APIs, types, and functions
- `smbd_setup_mdns_registration()` is the public setup API.
- With `WITH_DNSSD_SUPPORT`, `struct dns_reg_state` stores tevent context, port, `DNSServiceRef`, timer, socket fd, and fd event.
- `dns_register_smbd_schedule()` resets old registration state and schedules an immediate or delayed retry.
- `dns_register_smbd_retry()` calls `DNSServiceRegister()` and registers the DNS-SD socket with tevent.
- `dns_register_smbd_fde_handler()` processes mDNS daemon results and retries on failure.

## Control flow
Setup allocates a state object, installs a destructor, and schedules immediate registration. Each retry destroys any existing DNS-SD ref/timer/fd event, attempts registration on any interface with service type `_smb._tcp` and the configured port, then adds a tevent fd watcher for the DNS-SD socket. If registration or result processing fails, a new retry is scheduled five minutes later. On a successful processed result, the state object is freed.

## State and persistence behavior
The file holds transient tevent and DNS-SD registration state. Actual advertised service state is maintained by the local mDNS daemon while the `DNSServiceRef` is active. No repository or TDB state is written.

## Dependencies and integration points
It depends on Apple's/Avahi-compatible `dns_sd.h`, tevent timers/fds, and smbd startup code that calls `smbd_setup_mdns_registration()`. It supports browsing via SMB clients using service discovery.

## Risks and edge cases
- The destructor clears both timer and fd event and deallocates `DNSServiceRef`; retry code relies on this idempotence.
- Registration failures are logged and retried indefinitely at a fixed interval.
- The callback argument to `DNSServiceRegister()` is NULL, so only socket result processing errors are observed.
- Non-DNSSD builds silently report success.

## Test signals
Tests should build with and without DNSSD, verify immediate schedule, simulate registration failure and retry timer creation, process-result failure retry, destructor cleanup, and advertised `_smb._tcp` service visibility on DNSSD-capable systems.
