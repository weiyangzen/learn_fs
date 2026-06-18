# sources/security-integrity/selinux/libselinux/src/file_path_suffixes.h

Purpose: Central macro list of SELinux policy/config file path suffixes.

Important APIs/types/functions: the file is intended for inclusion with an `S_(NAME, suffix)` macro defined by the includer. Entries cover policy binary, contexts directories, file/media/X/db context files, default/failsafe contexts, seusers, translations, secolor, subs files, and service-specific context paths.

Control flow: no logic; inclusion expands the table according to caller-defined macro.

State and persistence: defines canonical relative paths under the SELinux policy root.

Dependencies and integration: used by internal path helper generation in `selinux_internal` code outside this subset.

Risks and test signals: path changes affect many public helper APIs. Tests should cover generated helper strings and compatibility of deprecated aliases such as `BOOLEANS` and `USERS_DIR`.
