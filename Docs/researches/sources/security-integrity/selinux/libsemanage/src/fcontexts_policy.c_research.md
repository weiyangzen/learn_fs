# sources/security-integrity/selinux/libsemanage/src/fcontexts_policy.c

Purpose: provides read-only policy-view APIs for file contexts and generated home-directory file contexts.

Important APIs/functions: `semanage_fcontext_query`, `exists`, `count`, `iterate`, `list`, and `semanage_fcontext_list_homedirs`. All normal policy APIs delegate to `semanage_fcontext_dbase_policy(handle)`; homedir listing delegates to `semanage_fcontext_dbase_homedirs(handle)`.

Control flow: functions are thin database dispatchers with no parsing or validation logic. They rely on the handle having initialized policy fcontext databases during connection.

State/persistence: reads policy plus local merged view from the policy fcontext database, and reads generated homedir contexts from the separate homedir database slot. It does not modify persistent state.

Dependencies/integration: called by consumers such as `genhomedircon.c` to test home-directory path conflicts and by Python wrapper tests to list fcontexts. Risks are incorrect database slot selection and caller misuse before connection. Tests should list policy fcontexts, query by key, and verify `list_homedirs` sees generated homedir output when enabled.
