# sources/security-integrity/selinux/python/semanage/seobject.py

## Purpose
`seobject.py` is the backend implementation for the `semanage` CLI. It wraps libsemanage Python bindings and SELinux/sepolicy/setools helpers to manage local policy customizations for modules, permissive domains, logins, SELinux users, ports, Infiniband pkeys/end ports, nodes, interfaces, file contexts, and booleans.

## Important APIs, types, and functions
- Global maps `file_types`, `file_type_str_to_option`, and `ftype_to_audit` translate CLI file-type names to libsemanage constants, CLI options, and audit-resource labels.
- `logger` has two implementations: an audit-backed implementation using `audit.audit_log_semanage_message()`/`audit.audit_log_user_comm_message()`, and a syslog fallback. `nulllogger` suppresses logging for alternate stores.
- `validate_level()`, `translate()`, and `untranslate()` validate and convert MLS/MCS labels through `selinux_*_context` APIs.
- `semanageRecords` owns the shared libsemanage handle, selected store, transaction flag, begin/commit/finish lifecycle, `--noreload`, and common error handling.
- Record classes implement object-specific operations:
  - `moduleRecords`: list/install/remove/enable/disable modules and reset disabled modules.
  - `dontauditClass`: toggles disable-dontaudit state.
  - `permissiveRecords`: creates/removes `permissive_<type>` CIL modules.
  - `loginRecords`: manages Linux login or `%group` mappings to SELinux users and ranges.
  - `seluserRecords`: manages SELinux users, roles, prefix, MLS level, and range.
  - `portRecords`: manages protocol/port or range to type/range mappings.
  - `ibpkeyRecords` and `ibendportRecords`: manage Infiniband pkey and end-port contexts.
  - `nodeRecords`: manages IPv4/IPv6 network node contexts.
  - `interfaceRecords`: manages network interface contexts.
  - `fcontextRecords`: manages file-context regexes and equivalence substitutions.
  - `booleanRecords`: manages persistent and active boolean values.

## Control flow
Each record class follows a common public pattern: `add()`, `modify()`, `delete()`, and `deleteall()` call `begin()`, run a private `__add`/`__modify`/`__delete`, then `commit()`. Add operations usually modify an existing record when one already exists. Delete operations usually refuse to remove non-local policy records. List and `customized()` methods query libsemanage lists and format either human-readable output or replayable semanage fragments.

The base constructor creates or reuses a process-global semanage handle, selects an alternate store when requested, connects to the store, records whether MLS is enabled in the global `is_mls_enabled`, and chooses an audit/syslog/no-op logger. `handleImport()` in the CLI uses `semanageRecords.start()` and `finish()` so nested record operations join one transaction instead of committing individually.

## State and persistence behavior
Persistent state is written to the SELinux policy store via libsemanage local customization APIs and `semanage_commit()`. The class-level `semanageRecords.handle`, `store`, and `transaction` make all record objects in a process share a connection and transaction state. `commit()` honors `--noreload` by calling `semanage_set_reload(self.sh, 0)` before committing. `fcontextRecords` has an additional persistence path: equivalence rules are loaded from `selinux_file_context_subs_path()` and `_dist_path()`, then local substitutions are rewritten through a temp file and `os.rename()` when `equal_ind` is set. `booleanRecords` may also set active runtime booleans with `semanage_bool_set_active()` when modifying the current store.

## Dependencies and integration points
This module imports `pwd`, `grp`, `selinux`, `os`, `re`, `sys`, `stat`, `socket`, `ipaddress`, `syslog`, `sepolicy`, `setools.policyrep.SELinuxPolicy`, `setools.typequery.TypeQuery`, and all names from the generated `semanage` libsemanage binding. The CLI depends on these classes and method signatures. SELinux policy state is also read through `selinux.getseuserbyname()`, `/logins` under the policy root, sepolicy attribute queries, setools type queries for Infiniband types, and boolean description/category helpers.

## Risks and edge cases
- The shared class-level handle and transaction flag make this module process-global and not safe for independent concurrent use in one interpreter.
- Alternate policy stores set global SELinux policy root with `selinux.selinux_set_policy_root()`, which can affect later calls in the same process.
- Many libsemanage return codes are checked, but some setter return values are ignored after query success, which can hide partial failures until commit.
- `ibpkeyRecords.__exists()` calls `.formnat(...)` on a string in one error path, producing `AttributeError` instead of the intended `ValueError` if key existence checking fails.
- `ibendportRecords.add()` formats a message with undefined `port` when an entry already exists, causing `NameError` on that path.
- In `moduleRecords.get_all()`, sorting is described as higher priorities first, but the first sort key is language extension and then name; priority ordering is not actually applied.
- `fcontextRecords.commit()` writes equivalence substitutions outside libsemanage's usual object API. It uses a temp file and rename, but does not explicitly fsync or lock the file.
- `booleanRecords.customized()` emits `-%s` using numeric active state values, producing `-0`/`-1`; that matches parser aliases but is less clear than `--off`/`--on`.
- Input validation is uneven across object types. Ports and pkeys parse integers and bound high values, while interface names and file regexes rely mostly on libsemanage acceptance.
- Audit logging uses `audit.audit_encode_nv_string()` in fcontext paths, but if the fallback logger is active the `audit` module name may not exist; these fcontext methods still refer to `audit` directly and can fail when the audit import failed.

## Test signals
`test-semanage.py` covers common fcontext, port, login, user, boolean, list, extract, and import/export paths. Coverage is absent or thin for Infiniband records, interface/node add/modify/delete, module enable/disable/remove, permissive domains, dontaudit, alternate stores, `--noreload`, audit fallback behavior, error-path typos, and fcontext equivalence conflict handling. Meaningful integration tests require root-like privileges, SELinux enabled/enforcing, libsemanage Python bindings, setools, sepolicy, and a mutable test policy store.
