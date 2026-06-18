# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/config.py

Purpose: central mutable configuration object for ntlmrelayx servers, clients, and attacks. `NTLMRelayxConfig` stores command-line-derived options and exposes setter methods used by main setup code. `parse_listening_ports()` parses comma-separated ports and ranges.

Important APIs and control flow: `__init__()` initializes defaults for interface/listening settings, target handling, SOCKS, SMB/RPC/LDAP/MSSQL/HTTP/WebDAV/AD CS/Shadow Credentials/SCCM attack options, protocol client registry, and attack registry. Most setters directly assign attributes. `setDomainAccount()` enforces machine account, hashes, and domain IP together and only applies when `remove_target` is enabled. `setRPCOptions()` parses SMB credentials and hashes. `parse_listening_ports()` accepts entries like `80,443,8000-8010` and returns a set of integers.

State and persistence: all state is in-memory and intentionally mutable. No disk I/O occurs. The config object is passed by reference to servers, protocol clients, and attacks.

Dependencies and integration: imports `parse_credentials`. It is the integration hub between CLI parsing, relay servers, protocol client factories, attack factories, SOCKS server, and target processors.

Risks and test signals: many attributes are created only by setters, so consumers can hit missing attributes if setup paths diverge. Port parsing does not enforce 1-65535. Tests should cover default values, each multi-option setter, domain account validation, hash splitting, WPAD enablement, exploit flags, and valid/invalid port lists including reversed ranges.
