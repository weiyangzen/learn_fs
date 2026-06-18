# sources/security-integrity/selinux/libsemanage/src/ibendports_policy.c

Purpose: provides policy-view read APIs for InfiniBand end-port records.

Important APIs: `semanage_ibendport_query`, `exists`, `count`, `iterate`, and `list`.

Control flow: each function selects `semanage_ibendport_dbase_policy(handle)` and calls the generic database operation. There is no parsing or validation logic here.

State/persistence: reads the active/tmp policydb-backed ibendport view initialized by `ibendports_policydb.c`. It does not modify persistent state.

Dependencies/integration: used by consumers of the public semanage ibendport policy API and by Python/binding tests where present. Risks are using before handle connection or missing backend initialization. Test signals are query/list/count against a policy containing ibendportcon rules.
