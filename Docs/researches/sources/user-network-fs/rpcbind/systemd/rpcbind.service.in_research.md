<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/systemd/rpcbind.service.in -->
# sources/user-network-fs/rpcbind/systemd/rpcbind.service.in

Purpose: Template for the systemd service unit that runs rpcbind under socket activation with hardening and optional warm-start/configuration substitutions.

Important directives: `DefaultDependencies=no`, `RequiresMountsFor=@statedir@`, `Requires=rpcbind.socket`, `Wants=rpcbind.target systemd-tmpfiles-setup.service`, and `After=systemd-tmpfiles-setup.service` align service startup with state directory preparation and the socket unit. `Type=notify` matches `sd_notify(READY=1)` in `rpcbind.c`. `ExecStart=@_sbindir@/rpcbind $RPCBIND_OPTIONS @warmstarts_opt@ -f` runs rpcbind in foreground for systemd supervision.

Control flow and integration: systemd starts or activates `rpcbind.socket` first, passes sockets to the daemon, reads optional environment files from `/etc/rpcbind.conf`, `/etc/default/rpcbind`, and `/etc/sysconfig/rpcbind`, then waits for notify readiness. The daemon's systemd socket handling expects separate IPv4/IPv6 sockets and foreground execution.

State and persistence: `RequiresMountsFor=@statedir@` ensures warm-start state storage is mounted before service start. Environment files can change daemon behavior via `RPCBIND_OPTIONS`.

Dependencies and security: Hardening directives include `ProtectSystem=full`, `ProtectHome=true`, `PrivateDevices=true`, hostname/clock/kernel/control-group protections, and `RestrictRealtime=true`. These reduce daemon access but must still allow configured state directory and socket operations.

Risks: Template substitutions must provide valid `@statedir@`, `@_sbindir@`, and `@warmstarts_opt@`. Overly restrictive hardening can break warm-start or platform-specific needs if state paths are not covered. Environment files are optional, so missing files are non-fatal.

Test signals: Validate generated unit with `systemd-analyze verify`, start with socket activation, confirm `READY=1`, verify warm-start path access, and test environment-file option propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/systemd/rpcbind.service.in -->
