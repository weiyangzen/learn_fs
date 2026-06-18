# sources/security-integrity/selinux/libsemanage/src/ibpkey_internal.h

Purpose: declares internal hooks for InfiniBand partition key records.

Important APIs: `SEMANAGE_IBPKEY_RTABLE`, `ibpkey_file_dbase_init/release`, `ibpkey_policydb_dbase_init/release`, `semanage_ibpkey_validate_local`, and `semanage_ibpkey_compare2_qsort`.

Control flow/integration: local stores use the file backend; policy views use the policydb backend; commit validation uses the local validator to reject overlapping pkey ranges per subnet prefix.

State/persistence: no state. Persistent data lives in local ibpkey text files and policydb records. Risks are declaration drift and qsort comparator misuse. Tests should include parser/backend initialization, range overlap rejection, and policy query/list behavior.
