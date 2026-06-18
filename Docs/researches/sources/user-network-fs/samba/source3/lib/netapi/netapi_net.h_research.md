# Research: sources/user-network-fs/samba/source3/lib/netapi/netapi_net.h

Purpose: small private header shared between the Samba `net` binary and `libnetapi`. It exposes a context initialization path that reuses already-loaded configuration and credentials instead of doing the full public library initialization sequence.

Important APIs/types: declares `libnetapi_net_init(struct libnetapi_ctx **ctx, struct loadparm_context *lp_ctx, struct cli_credentials *creds)`. The API returns `NET_API_STATUS` and installs the supplied `loadparm_context` and `cli_credentials` into a new `libnetapi_ctx`.

Control flow: no runtime control flow is present in the header. Callers include it when they need the specialized initialization mode, typically after Samba command-line/config parsing has already populated loadparm and credential state.

State and persistence: no storage is defined here. The function it declares affects process-local `libnetapi_ctx` state by wiring existing configuration and credentials into the NetAPI layer. It does not by itself persist anything.

Dependencies/integration: included by `netapi_private.h`, which lets private implementation code know about this initialization contract. It bridges command-line Samba tooling and the library API without forcing a second config read or debug/log setup.

Risks: because the header says it is private between `net` and `libnet`, external consumers should not rely on this ABI. Passing credentials/loadparm with lifetimes shorter than the resulting context would be hazardous unless the implementation takes references. The comment contains a duplicated "and", indicating the file is intentionally minimal rather than heavily maintained.

Test signals: tests should initialize libnetapi through both public `libnetapi_init` and private `libnetapi_net_init` paths and verify credentials, workgroup, Kerberos mode, and loadparm-derived behavior match expectations.
