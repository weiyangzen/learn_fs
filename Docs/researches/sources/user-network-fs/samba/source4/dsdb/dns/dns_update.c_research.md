# sources/user-network-fs/samba/source4/dsdb/dns/dns_update.c

## Purpose

`dns_update.c` registers Samba's `dnsupdate` task service for Active Directory domain controllers. The service periodically runs configured helper commands to update DC DNS names and SPNs, and exposes an IRPC endpoint used by netlogon to request RODC DNS updates for a specific read-only domain controller.

## Important APIs, Types, and Functions

- `struct dnsupdate_service` stores task context, system session credentials, local `samdb`, and periodic command state for configuration/name updates.
- `dnsupdate_check_names()` starts the configured `dns update command` and `spn update command` asynchronously through `samba_runcmd_send()`.
- `dnsupdate_nameupdate_done()` and `dnsupdate_spnupdate_done()` receive command completion and log success/failure.
- `dnsupdate_nameupdate_schedule()` and `dnsupdate_nameupdate_handler_te()` implement the `dnsupdate:name interval` tevent timer.
- `struct dnsupdate_RODC_state` tracks an async RODC update request, temporary files, and the deferred IRPC reply.
- `dnsupdate_dnsupdate_RODC()` validates the target RODC, writes requested DNS records to a temporary update-list file, launches the DNS update command with `--update-list` and `--update-cache`, and defers the IRPC reply until completion.
- `dnsupdate_task_init()` starts the service only on AD DCs, connects to samdb as system, runs the first update, schedules periodic updates, and registers the `"dnsupdate"` IRPC name and `DNSUPDATE_RODC` handler.
- `server_service_dnsupdate_init()` registers the task service.

## Control Flow

Service initialization rejects non-AD-DC roles, creates service state, obtains `system_session()`, opens local samdb, reads the name-update interval (default 600 seconds), performs an immediate DNS/SPN update, schedules the next timer, and registers IRPC. On each timer, the handler calls `dnsupdate_check_names()` and reschedules itself.

For regular updates, existing DNS update child state is freed before starting a new DNS update command. The code then starts the SPN update command independently. Both commands have a 20 second startup timeout and use callbacks to clear request pointers and log exit status.

For RODC updates, the IRPC handler creates a temporary update-list file and a cache path. It maps the incoming domain SID to a DN, finds the RODC site and NTDS GUID, reads `dNSHostName`, and writes only supported `NL_DNS_NAME_INFO` record types as SRV or CNAME update instructions. It then closes the file, launches the DNS update command with file arguments, marks the IRPC message as deferred, and replies from `dnsupdate_RODC_callback()`. The callback maps command failure to an NTSTATUS result and applies that status to every returned DNS name entry.

## State and Persistence Behavior

The service does not directly modify DNS zones; persistence is delegated to the configured helper scripts and their caches. It reads samdb for RODC site, NTDS GUID, and hostname. Temporary update-list and cache files are owned by `dnsupdate_RODC_state`; the destructor closes the fd if still open and unlinks both paths. Periodic state is in-memory tevent timers and child requests.

## Dependencies and Integration Points

This task integrates with Samba service registration, `samba_runcmd`, loadparm command settings, samdb helpers, netlogon IRPC, and the external `samba_dnsupdate`/SPN update commands. It depends on AD DC role configuration and local system credentials.

## Risks

Command execution and temporary file handling are the primary operational risks. A failed helper command only logs and retries later, so persistent misconfiguration can leave DNS/SPN data stale. The regular DNS update frees only `nameupdate.subreq` before launching a new run, so concurrent SPN update handling depends on the previous SPN request lifetime and command behavior. RODC requests trust the input DNS-name type enum and write update lines; future enum additions need explicit handling. Error mapping in command callbacks uses `sys_errno` as the logged exit code, so diagnostics may be confusing if the helper exits normally with a nonzero status.

## Test Signals

Tests should assert service startup behavior by role, interval scheduling, immediate command launch, callback cleanup, and graceful command failure. RODC tests should cover missing site, missing NTDS GUID, missing `dNSHostName`, each supported DNS name type, temporary-file cleanup on early errors, deferred IRPC reply, and per-name result propagation.
