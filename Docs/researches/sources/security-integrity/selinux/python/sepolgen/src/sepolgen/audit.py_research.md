# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/audit.py

## Purpose
This module obtains and parses SELinux-related audit messages, converts AVC denials/grants and invalid SID messages into sepolgen access and role-type models, and optionally filters them. It bridges host audit logs, kernel messages, `audit2why`, and policy-generation input structures.

## Important APIs, types, and functions
- `get_audit_boot_msgs()`, `get_audit_msgs()`, and `get_dmesg_msgs()` run `/sbin/ausearch` or `/bin/dmesg` and return decoded text.
- `AuditMessage` is the base parser for audit headers.
- `InvalidMessage`, `PathMessage`, `AVCMessage`, `PolicyLoadMessage`, `DaemonStartMessage`, and `ComputeSidMessage` represent specific SELinux/audit record types.
- `AVCMessage.from_split_string()` parses source/target contexts, class, command, executable, name, ioctl command, access set, denial/grant status, and calls `analyze()`.
- `AVCMessage.analyze()` caches `audit2why.analyze()` results in global `avcdict` and converts several audit2why error types to `ValueError`.
- `AuditParser` stores parsed messages, supports last-policy-load-only resets, groups records by audit header, attaches AVC_PATH paths to matching AVCs, and exposes `parse_file()`, `parse_string()`, `to_role()`, and `to_access()`.
- `AVCTypeFilter` and `ComputeSidTypeFilter` include messages whose source, target, or invalid type matches a regex.

## Control flow
Message collection helpers shell out to audit/dmesg commands. Parsing splits each input line into whitespace records, scans for SELinux-related markers, instantiates the appropriate message class, and asks it to parse the same split records. High-level parsing stores recognized messages by class; `PolicyLoadMessage` or auditd `DaemonStartMessage` can reset accumulated state when `last_load_only` is enabled. After parsing, `__post_process()` uses shared audit headers to copy `AVC_PATH` paths onto AVC messages. `to_access()` filters AVCs, skips granted records by default, creates `access.AccessVector` objects, attaches audit2why metadata and ioctl xperms, then adds them to an `AccessVectorSet`.

## State and persistence behavior
Parser state is in-memory: message lists, `by_header`, and `check_input_file`. The module-level `avcdict` caches audit2why analysis results by source context, target context, class, and access tuple. There is no persistence, but host reads depend on `/proc/uptime`, audit logs, and dmesg. `parse_file()` exits the process with status 0 after printing "Nothing to do" if no SELinux-related records were found.

## Dependencies and integration points
The module imports `re`, `sys`, local `refpolicy`, `access`, and `util`, plus `selinux.audit2why`. It calls `/sbin/ausearch` and `/bin/dmesg` through `subprocess`. It depends on `refpolicy.SecurityContext` parsing and `access.AccessVectorSet`/`RoleTypeSet`.

## Risks and edge cases
- `get_audit_boot_msgs()` has `fd.close` without parentheses, so the `/proc/uptime` descriptor is not explicitly closed.
- `AuditParser.__parse_line()` creates `DaemonStartMessage(list)` instead of passing the line string; this stores the built-in `list` object as the raw message.
- `AVCMessage.analyze()` checks `BADSCON` twice; the second branch message says "Invalid Type Class" and probably intended a different audit2why constant.
- Parsing is whitespace-oriented and only handles the subset of audit fields this module needs. Quoted values with embedded spaces or unusual audit formatting can be lost.
- `parse_file()` calls `sys.exit(0)` on no input, making the parser awkward as a library in callers that expect an empty result.
- The global analysis cache is unbounded and process-global.
- Errors from missing `/sbin/ausearch` or `/bin/dmesg` propagate from `subprocess.Popen`.

## Test signals
Useful tests would feed sample AVC, granted AVC, AVC_PATH, MAC_POLICY_LOAD, DAEMON_START, and security_compute_sid lines into `parse_string()`, verify list resets with `last_load_only`, verify path post-processing by audit header, and check `to_access()` output including ioctl xperms. Host command helpers require privileged/system integration tests or subprocess mocking.
