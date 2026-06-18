# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nsm.c

Purpose: provides XDR routines for Network Status Monitor structures used with NLM recovery and host monitoring.

Important APIs and types: `xdr_res()`, `xdr_sm_stat_res()`, `xdr_sm_stat()`, `xdr_my_id()`, `xdr_mon_id()`, `xdr_mon()`, `xdr_notify()`, and protocol types from `nsm.h`.

Control flow: routines encode/decode enum results, state integers, monitor identity fields, program/version/procedure callback identity, monitor payload private bytes, and notify messages in fixed protocol order. Strings are bounded by `SM_MAXSTRLEN`; monitor private data is fixed-size opaque bytes.

State and persistence: no local state. State numbers are protocol data used by recovery/monitoring layers elsewhere.

Dependencies and integration points: depends on ntirpc XDR and `nsm.h`. Integrates with NLM/NSM code that tracks client reboot notifications and lock reclamation.

Risks: NSM identity strings and callback program values are trusted only after higher-layer validation. Decode failures must release any allocated strings through the normal XDR free path.

Test signals: round-trip monitor, notify, stat, and stat result structures; oversized monitor names; corrupted opaque private payload length; and XDR_FREE after decoded strings.
