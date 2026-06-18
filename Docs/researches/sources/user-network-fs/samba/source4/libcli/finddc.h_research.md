# sources/user-network-fs/samba/source4/libcli/finddc.h

Purpose: declares the shared input/output structure for finding domain controllers and includes generated prototypes for the find-DC API.

Important type: `struct finddcs` contains input protocol, domain name, optional site name, optional domain SID, required `DS_SERVER_*` flags, and optional server address override. Output contains selected server IP address and `netlogon_samlogon_response`.

Control flow contract: callers fill `io.in`, call a protocol-specific find routine such as CLDAP, and read `io.out` when `NT_STATUS_OK` is returned.

State and persistence: the structure is caller-owned and transient. No persistent state is defined.

Dependencies and integration: includes messaging, `libcli.h`, Netlogon, and loadparm types, then includes `finddcs_proto.h`. The key integration is with CLDAP Netlogon pings and name resolution.

Risks: optional inputs must be interpreted consistently by implementations. A missing domain name and server address is invalid. Test signals include combinations of DNS domain, NetBIOS domain, explicit IP, explicit hostname, site names, domain SID filters, and minimum DC flag filters.
