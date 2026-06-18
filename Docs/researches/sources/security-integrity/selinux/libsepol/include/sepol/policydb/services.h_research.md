# sources/security-integrity/selinux/libsepol/include/sepol/policydb/services.h

Purpose: Declares the internal/public security-server style service API over policydb and SID tables.

Important APIs and functions: Set/load policy state; compute AV decisions and denial reasons/buffers; validate transitions; class/permission name mapping; transition/member/change SID computation; SID/context conversion; user SID enumeration; fs/port/ibpkey/ibendport/netif/node/genfs labeling lookups.

Control flow: Callers load or set policydb/sidtab, then request decisions or labeling SIDs. Service code consults avtabs, constraints, RBAC, bounds, ocontexts, genfs, and sidtab mappings.

State and persistence: Can use explicit caller-provided policydb/sidtab or private global structures initialized by `sepol_load_policy`/`sepol_set_policydb_from_file`.

Dependencies and integration points: Used by checkpolicy-like tools, deprecated context checks, and consumers needing userspace SELinux decisions.

Risks: Global fallback state is hard to isolate. Returned buffers/SIDs require caller ownership discipline. Decision reasons are security-sensitive diagnostics.

Test signals: AV decisions, constraint reason buffers, transition SID creation, and all ocontext lookup types need coverage.
