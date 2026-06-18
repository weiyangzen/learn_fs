<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/audit2allow -->
# sources/security-integrity/selinux/python/audit2allow/audit2allow

## Purpose
Converts SELinux audit denials into allow/dontaudit policy, reference-policy interface calls, CIL, loadable module packages, or human-readable `audit2why` explanations.

## Important APIs, Types, And Functions
The central class is `AuditToPolicy` with methods `__parse_options()`, `__read_input()`, `__process_input()`, `__load_interface_info()`, `__output_modulepackage()`, `__output_audit2why()`, `__output()`, and `main()`. It uses `sepolgen.audit`, `policygen`, `interfaces`, `output`, `objectmodel`, `defaults`, `module`, `selinux.audit2why`, and optional `sepolicy` boolean descriptions.

## Control Flow
Options choose audit source (`stdin`, file, dmesg, audit log, boot audit), policy path, module/package output, CIL, reference-policy generation, xperms, explanation verbosity, type filters, and audit2why mode. Input is parsed to AVC accesses and role transitions. Normal output configures a `PolicyGenerator`, optionally loads interface and permission maps, adds access/role data, and writes to stdout, append file, or `.te` plus compiled `.pp`. Audit2why mode initializes the audit2why engine and prints cause-specific explanations for allow/dontaudit/boolean/TE/constraint/RBAC/bounds outcomes.

## State And Persistence
It may read audit logs/dmesg, append output files, create `.te` and `.pp` module-package artifacts, and initialize/finish the audit2why analysis engine.

## Dependencies And Integration Points
It integrates audit records, active or supplied binary policy, sepolgen reference data, module compiler tooling, and `semodule -i` deployment guidance.

## Risks And Edge Cases
Conflict checks print errors but do not always exit immediately. Generated policy may be overly broad if audit input is noisy. Module package mode refuses output/module/CIL combinations. Missing interface or perm-map files abort reference-policy output.

## Test Signals
Use supplied dummy policy/log tests, xperm generation, module name validation, each input source, CIL and reference/no-reference modes, module package output, and audit2why boolean/constraint cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/audit2allow -->
