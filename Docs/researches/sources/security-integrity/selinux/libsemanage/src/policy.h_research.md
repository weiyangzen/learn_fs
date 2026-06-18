# sources/security-integrity/selinux/libsemanage/src/policy.h

Purpose: defines the backend dispatch table for policy/store operations and declares backend-independent component merge/commit functions.

Important types/APIs: `struct semanage_policy_table` contains function pointers for serial, destroy, disconnect, begin transaction, commit, module install/install_file/extract/remove/list, enabled status, module info/list-all/install-info/remove-key. It also declares `semanage_base_merge_components` and `semanage_commit_components`.

Control flow/integration: `handle.c` and `modules.c` call these function pointers after connection selects a backend, currently direct store. Backend implementations populate the table to simulate polymorphism in C.

State/persistence: no state in the header, but function pointers mediate all persistent policy/module operations. Risks include NULL function pointers for unsupported operations and ABI changes when adding backend capabilities. Test signals are backend connection tests, module operation dispatch, and commit/transaction flows.
