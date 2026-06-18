# sources/security-integrity/selinux/libselinux/src/audit2why.c

Purpose: `audit2why.c` implements the Python C extension module `audit2why`, which explains why an AVC denial occurred by loading a binary SELinux policy with libsepol, translating contexts/classes/permissions into policy identifiers, and computing denial reasons.

Important APIs/types/functions: exported Python methods are `init`, `analyze`, and `finish`. Module constants include `ALLOW`, `DONTAUDIT`, `TERULE`, `BOOLEAN`, `CONSTRAINT`, `RBAC`, `BOUNDS`, and error codes like `BADSCON`. Internal state is held in global `struct avc_t *avc`, global `sidtab`, `boollist`, and `boolcnt`. `__policy_init()` reads policy, initializes `sepol_policydb_t`, `sepol_handle_t`, booleans, and sidtab. `analyze()` calls `sepol_compute_av_reason_buffer()`. `check_booleans()` temporarily toggles each policy boolean to find changes that would allow access.

Control flow: `init()` refuses repeated initialization, selects an explicit policy path or `selinux_current_policy_path()`, reads policydb, loads booleans, and sets libsepol globals. `analyze()` parses five Python arguments, converts source/target contexts and permissions, computes an access vector decision and reason mask, then returns either a reason constant plus `None`, a constraint string, or a boolean list. `finish()` releases all global policy state.

State and persistence: state is process-global and persists until `finish()` or module teardown. Boolean probing mutates the in-memory policydb and attempts to restore each boolean before continuing. No on-disk policy is modified.

Dependencies and integration: uses Python C API, libsepol policydb/services APIs, libselinux policy path helpers, and raw SELinux context strings. It is built as `audit2why.so` by the makefile and consumed by audit analysis tooling.

Risks and test signals: the extension is not reentrant because policy state is global. Boolean probing has many early exits where restoration and object cleanup matter. Tests should cover missing policy, invalid contexts/classes/perms, constraint/RBAC/bounds reasons, boolean-caused allow decisions, repeated init rejection, finish idempotence, and Python reference ownership.
