# sources/security-integrity/selinux/libsemanage/src/modules.h

Purpose: internal module-management declarations shared by handle, policy, direct backend, and module implementation code.

Important types/APIs: `struct semanage_module_info` with priority/name/lang_ext/enabled; `struct semanage_module_key` with priority/name; init/clone/validation helpers; `semanage_string_to_priority`; module path type enum for priority/name/hll/cil/lang_ext/disabled; `semanage_module_get_path`; checksum constants and `semanage_hash_to_checksum_string`; legacy upgrade/install-base declarations.

Control flow/integration: backend-independent code uses these structs as module identifiers and metadata. Direct store code uses the path enum to derive on-disk module layout paths.

State/persistence: the structs own heap strings but this header only declares layout and functions. Risks include ABI/layout changes and path enum mismatch with `modules.c`. Test signals are compile coverage, public module API tests, and path generation for all enum values.
