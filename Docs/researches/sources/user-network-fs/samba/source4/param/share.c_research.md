# sources/user-network-fs/samba/source4/param/share.c

Purpose: `share.c` implements the generic share configuration backend registry and forwarding API.

Important APIs, types, and functions: It exports option accessors `share_string_option`, `share_int_option`, `share_bool_option`, `share_string_list_option`; lifecycle APIs `share_list_all`, `share_get_config`, `share_create`, `share_set`, `share_remove`; registry APIs `share_register`, `share_get_context`, and `share_init`.

Control flow: Option and CRUD functions dispatch through the selected `share_ops`. Optional create/set/remove return `NT_STATUS_NOT_IMPLEMENTED` when absent. Registration rejects duplicate names, reallocates the global backend vector, copies the ops table, and stores a duplicated backend name. `share_get_context` currently selects the `classic` backend.

State and persistence behavior: Registered backends are process-global heap state. Actual share persistence depends on backend implementation; the classic backend reads loadparm and does not implement mutations.

Dependencies and integration points: It depends on `param/share.h`, loadparm types, Samba module initialization, and static share module tables. NTVFS backends use share option accessors heavily.

Risks: The backend list uses manual allocation outside talloc and panics on OOM. `share_get_context` is hard-wired to `classic`, limiting backend configurability. No synchronization is visible around backend registration.

Test signals: Existing local share tests exercise context creation and unsupported mutation paths. Additional tests should cover duplicate backend registration, missing classic backend, and option dispatch through a fake backend.
