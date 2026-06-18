# sources/security-integrity/selinux/libsemanage/src/ports_policy.c

Purpose: policy-view read APIs for network port records.

Important APIs: `semanage_port_query`, `exists`, `count`, `iterate`, and `list`.

Control flow: each function selects `semanage_port_dbase_policy(handle)` and delegates to generic database operations.

State/persistence: reads policydb-backed port data only. Dependencies are handle database selectors and initialized policydb backend.

Risks: no extra validation or transformation is performed, so correctness is in the record/policydb layers. Test signals include list/query/count with tcp/udp/dccp/sctp policy records and absent-key behavior.
