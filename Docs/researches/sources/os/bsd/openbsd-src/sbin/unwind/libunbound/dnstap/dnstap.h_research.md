# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnstap/dnstap.h

Conditional dnstap interface header for Unbound. Contents are compiled only when `USE_DNSTAP` is defined.

Important point for this build:
- `dnstap_config.h` leaves `USE_DNSTAP` disabled, so these declarations are inactive in the OpenBSD `unwind` build.

When enabled, defines:
- `struct dt_env`: dnstap I/O thread, per-worker message queue, identity/version strings, enabled message-type flags, sample lock/rate/counter.

API when enabled:
- create/apply/init/deinit/delete dnstap environment.
- apply log configuration.
- emit client query/response messages.
- emit resolver/forwarder outside query/response messages.

Role in group:
- Dormant optional telemetry interface retained from Unbound.
