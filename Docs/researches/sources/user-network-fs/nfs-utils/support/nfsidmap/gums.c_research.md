# sources/user-network-fs/nfs-utils/support/nfsidmap/gums.c

Purpose: optional libnfsidmap plugin that maps SPKM3/X.509/VOMS-authenticated principals to local UID/GID through a GUMS/PRIMA SAML identity mapping service.

Important APIs and data: plugin entry `libnfsidmap_plugin_init()` returns `gums_trans`, whose `.init` is `gums_init()` and `.princ_to_ids` is `gums_gss_princ_to_ids()`. `plugin_config_params conf` holds SAML schema, cert/key, CA directory, GUMS server URL, VOMS directory, and log level.

Control flow: `gums_init()` reads PRIMA config from `nfsidmap_config_get("GUMS", "Conf_File")` or `/etc/grid-security/prima-authz.conf`, extracts server/cert/key/schema/log/CA/VOMS settings, fills defaults, and validates required fields. Mapping accepts only `secname == "spkm3"`, decodes extra X.509 certificate blobs into user cert and chain, retrieves VOMS attributes, initializes PRIMA SAML support, builds a SAML request from server DN and user/VOMS FQANs, queries the mapping service, processes the response into local user/group names, then resolves them with `getpwnam_r()`/`getgrnam_r()`.

State and persistence: process-global `conf` stores plugin configuration. Persistent inputs include PRIMA config, service certificate/key, CA/VOMS directories, user proxy/certificate data, local NSS password/group databases, and the remote GUMS service. Test-program code can use `X509_USER_PROXY`.

Dependencies and integration: depends on OpenSSL X509/BIO APIs, VOMS, PRIMA logger/SOAP/SAML libraries, and libnfsidmap plugin interfaces. It integrates as a GSS-specific translation method.

Risks: `USING_TEST_PROGRAM` is defined in source, which defines `idmap_log_func`, `idmap_verbosity`, and a `main()` test harness in this file; build configuration must prevent conflicts if this is unintended. Several `strdup()` assignments can overwrite existing `conf` pointers on repeated init. External network/certificate/SAML dependencies make error handling and test determinism hard. `queryIdentityMappingService()` returning NULL leaves `local_uid` NULL and then `translate_to_uid(local_uid, ...)` would fail via `getpwnam_r()` expectations; the preceding response branch does not explicitly reject NULL response before translation.

Test signals: missing/malformed PRIMA config, default CA/VOMS dirs, SPKM3-only rejection, DER certificate parsing, VOMS absent vs present, SAML request contents, GUMS response with uid/gid, local NSS lookup failures, cert/key errors, and repeated init/cleanup.
