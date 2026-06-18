# sources/user-network-fs/samba/source4/cldap_server/wscript_build

Purpose: Waf build definitions for the CLDAP service module and helper subsystem.

Important targets: `service_cldap` builds `cldap_server.c` as a `service` module with init function `server_service_cldapd_init`, module metadata, and deps `CLDAPD process_model netif`. `CLDAPD` builds `rootdse.c`, generates `proto.h`, and depends on `cli_cldap` and `ldbsamba`.

Control flow/state: the service target registers startup logic; the subsystem target supplies rootDSE request handling and generated prototypes consumed by the header. Build metadata only; no runtime state.

Dependencies/integration: links CLDAP service code to Samba's process model, network-interface handling, CLDAP client/server library, and LDB Samba helpers.

Risks/test signals: missing `CLDAPD` dependency or autoproto generation would break `cldap_server.h` consumers. Module metadata determines whether the service can be loaded. Build success and AD DC service startup tests validate this wiring.
