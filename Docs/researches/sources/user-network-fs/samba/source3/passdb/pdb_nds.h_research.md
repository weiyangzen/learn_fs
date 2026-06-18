# sources/user-network-fs/samba/source3/passdb/pdb_nds.h

Purpose: declares the NDS/eDirectory LDAP password helper API and backend registration entry point used by the base LDAP passdb code.

Important APIs/types/functions: it forward-declares `struct smbldap_state` and exposes `pdb_nds_get_password`, `pdb_nds_set_password`, and `pdb_nds_init`. The get function accepts an LDAP state, object DN, in/out password length, and output buffer. The set function accepts LDAP state, object DN, and clear text password. The init function registers `NDS_ldapsam`.

Control flow: `pdb_ldap.c` includes this header so `init_sam_from_ldap` can retrieve NDS passwords and `ldapsam_modify_entry` can set NDS passwords when the shared private state is marked as NDS. `pdb_ldapsam_init` also calls `pdb_nds_init` to register the alternate backend.

State and persistence behavior: this header has no state, but its functions read and write persistent eDirectory password state and may expose clear text password material to callers for hash generation.

Dependencies/integration: depends on Samba `NTSTATUS`, `TALLOC_CTX`, `smbldap_state`, and LDAP integer result conventions through surrounding includes. It is intentionally small so the base LDAP backend can call NDS-specific behavior without pulling implementation details into `pdb_ldap.c`.

Risks and test signals: callers must provide a correctly sized password buffer and must scrub sensitive output after use. Build tests should ensure the declarations remain consistent with `pdb_nds.c`; integration tests should verify NDS password retrieval/set behavior through the `NDS_ldapsam` backend rather than only through direct helper calls.
