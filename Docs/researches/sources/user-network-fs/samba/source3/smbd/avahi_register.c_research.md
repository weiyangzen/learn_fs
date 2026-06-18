# sources/user-network-fs/samba/source3/smbd/avahi_register.c

Purpose: registers Samba SMB, Time Machine disk, and device-info services with Avahi/mDNS for discovery by clients.

Important functions and APIs: defines `struct avahi_state_struct` holding Avahi poll, client, entry group, and SMB port. Provides a custom Avahi allocator backed by talloc (`avahi_allocator_malloc/free/realloc/calloc`) and installs it with `avahi_set_allocator`. `avahi_entry_group_callback()` logs group states. `avahi_client_callback()` handles Avahi client states and, when running, creates an entry group, registers `_smb._tcp`, optionally registers `_adisk._tcp` TXT records for shares with `fruit:time machine = yes`, registers `_device-info._tcp` with `fruit:model`, and commits the group. `avahi_start_register()` allocates state, creates a tevent-backed Avahi poll object, and starts an `AvahiClient`.

Control flow: Avahi drives asynchronous callbacks through the tevent poll bridge. On `AVAHI_CLIENT_S_RUNNING`, service registration is built from current loadparm state. On disconnected client failure, the code frees and recreates the Avahi client. Errors during any registration step log a debug message, free the entry group, and stop that registration attempt.

State and persistence: runtime-only mDNS registration state lives in Avahi client/entry-group objects under the supplied talloc context. It reads Samba configuration but does not persist settings.

Dependencies and integration: compiled when Avahi support is available; includes Avahi client/publish/common headers and `smbd/smbd.h`. It integrates with Samba loadparm (`lp_numservices`, `lp_snum_ok`, `lp_parm_bool`, `lp_const_servicename`, `lp_mdns_name`, `lp_netbios_name`, `lp_parm_const_string`) and tevent via `tevent_avahi_poll`.

Risks and test signals: `avahi_allocator_ctx` is global, so allocator lifetime and multiple registrations require care. Registration failure frees the whole entry group, which can remove already-added services. The `_adisk` TXT list grows from share enumeration and must be freed on all paths. Runtime signals are debug logs for Avahi state transitions and visible mDNS records for `_smb._tcp`, `_adisk._tcp`, and `_device-info._tcp`.
