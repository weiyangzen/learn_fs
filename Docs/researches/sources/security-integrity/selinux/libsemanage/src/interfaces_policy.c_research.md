# sources/security-integrity/selinux/libsemanage/src/interfaces_policy.c

Purpose: policy-view read APIs for network-interface records.

Important APIs: `semanage_iface_query`, `exists`, `count`, `iterate`, and `list`.

Control flow: thin wrappers select `semanage_iface_dbase_policy(handle)` and delegate to generic database methods.

State/persistence: reads policydb-backed interface data and does not modify stores. Dependencies are the handle database selector and the initialized policydb backend.

Risks: no local error handling beyond generic database return codes. Test signals include listing interfaces through C and Python bindings, querying absent/present keys, and count consistency with iteration.
