# sources/security-integrity/selinux/libsemanage/src/modules.c

Purpose: implements public module-management APIs, module info/key object helpers, module path construction, validation, and checksum computation.

Important APIs/functions: install/install_file/extract/remove/list wrappers, legacy upgrade compatibility, `semanage_module_info_*`, `semanage_module_key_*`, `semanage_module_get_path`, `semanage_module_get_enabled`, `set_enabled`, `semanage_string_to_priority`, validators for priority/name/enabled/lang extension, module info/list-all/install-info/remove-key APIs, `semanage_hash_to_checksum_string`, and `semanage_module_compute_checksum`.

Control flow: mutating module APIs require a connected handle and open a transaction automatically if needed, then set `sh->modules_modified` before delegating to the backend function table. Info/key setters validate inputs and duplicate owned strings. Path generation chooses active versus tmp module roots based on `sh->is_in_transaction` and composes priority/name/hll/cil/lang_ext/disabled paths. Checksum computation extracts module data, hashes it with SHA-256, and unmaps extracted data.

State/persistence: persistent module state lives in the semanage module store and is mutated by backend functions. This file owns heap strings in module info/key structs and updates handle transaction/module flags.

Risks: callers must destroy/free created structs correctly; validation regexes are hand-coded; automatic transaction start changes handle state; checksum assumes extracted data is mmap-backed and uses `munmap`. Tests should cover validators, path truncation, transaction auto-start, backend dispatch failure when disconnected, clone/destroy ownership, checksum length query, and install/remove/list flows.
