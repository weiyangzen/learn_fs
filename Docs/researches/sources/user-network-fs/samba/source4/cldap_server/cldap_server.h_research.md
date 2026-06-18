# sources/user-network-fs/samba/source4/cldap_server/cldap_server.h

Purpose: declares CLDAP server shared structures and imports generated prototypes.

Important types: `struct cldapd_server` contains the owning `task_server` and the SAMDB `ldb_context`. It forward-declares `struct ldap_SearchRequest` and includes `cldap_server/proto.h`.

Control flow/integration: used by `cldap_server.c` and `rootdse.c` to share the service context and function prototypes. It includes CLDAP and LDAP client/server types needed by handler signatures.

State/dependencies: defines in-memory service state only; persistence is whatever SAMDB context points at. Depends on `libcli/cldap/cldap.h`, `libcli/ldap/libcli_ldap.h`, and generated autoproto output from the build.

Risks/test signals: the small context structure is shared across synchronous request handling; adding per-request state here would risk leakage across clients. Generated proto inclusion means build ordering must produce `proto.h`. Compile coverage comes through `service_cldap` and `CLDAPD`.
