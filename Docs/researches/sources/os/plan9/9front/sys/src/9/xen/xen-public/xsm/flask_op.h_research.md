# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/xsm/flask_op.h

Purpose: Xen XSM/FLASK security-module operation ABI. It defines command payloads for policy loading, enforcement, SID/context conversion, access checks, transitions, users, booleans, AVC stats, object contexts, peer SID lookup, and domain relabeling.

Key interfaces:
- `XEN_FLASK_INTERFACE_VERSION`.
- Payloads: `xen_flask_load`, `xen_flask_setenforce`, `xen_flask_sid_context`, `xen_flask_access`, `xen_flask_transition`, `xen_flask_userlist`, `xen_flask_boolean`, stats/relabel structs.
- Top-level `xen_flask_op` with `FLASK_*` command constants.

Integration notes: Assumes Xen guest-handle and event-channel types are already visible through including context; this file itself does not include `xen.h`.

Risk/attention points: The missing local include means include order matters. It should be included only after types like `XEN_GUEST_HANDLE` and `evtchn_port_t` are defined.
