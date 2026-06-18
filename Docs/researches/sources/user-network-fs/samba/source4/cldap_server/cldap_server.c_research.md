# sources/user-network-fs/samba/source4/cldap_server/cldap_server.c

Purpose: implements the CLDAP server task for Samba AD DC locator/rootDSE queries over UDP/389.

Important APIs/functions: `server_service_cldapd_init()` registers the service. `cldapd_task_init()` validates role/interfaces, opens SAMDB, and starts sockets. `cldapd_startup_interfaces()` chooses wildcard and interface-specific binds. `cldapd_add_socket()` binds a CLDAP socket and installs the incoming handler. `cldapd_request_handler()` validates incoming LDAP message shape.

Control flow: startup loads interfaces and refuses standalone/member-server roles. On AD DCs it creates `cldapd_server`, opens SAMDB with `system_session()`, binds wildcard addresses unless `bind interfaces only` is set, then binds each configured interface. Runtime handling ignores AbandonRequest, rejects non-search requests, non-empty base DN, and non-base scope with LDAP operations errors, and dispatches valid requests to `cldapd_rootdse_request()`.

State/dependencies/integration: service lifetime state is task plus SAMDB context. Uses Samba service/task registration, CLDAP library, tsocket, network interface helpers, SAMDB, loadparm role config, system session auth, and IRPC naming.

Risks/test signals: binding UDP/389 can fail per-interface; request validation is strict because CLDAP clients retry on silence. The shared SAMDB context relies on rootDSE code clearing request-specific opaque state. Coverage is primarily AD DC CLDAP integration.
