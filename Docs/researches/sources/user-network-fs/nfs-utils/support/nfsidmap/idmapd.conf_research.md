# sources/user-network-fs/nfs-utils/support/nfsidmap/idmapd.conf

Purpose: sample/default configuration file for NFSv4 idmapping.

Important sections and options: `[General]` covers verbosity, NFSv4 domain, no-strip behavior for multi-domain identities, group-name reformatting, and local Kerberos realms. `[Mapping]` defines nobody user/group. `[Translation]` selects ordered mapping plugins via `Method` and optional `GSS-Methods`. `[Static]` provides literal GSS principal-to-local mappings. `[UMICH_SCHEMA]` documents LDAP server, search bases, TLS/SASL options, and schema attribute mappings.

Control flow: the file is consumed by `conffile.c` and `libnfsidmap.c`; comments describe defaults when options are omitted. Plugin modules read their own sections, for example static, LDAP, or GUMS.

State and persistence: persistent administrator configuration, normally installed under `/etc/idmapd.conf`. Values affect process-global libnfsidmap initialization and plugin behavior.

Dependencies and integration: integrates NFSv4 id-to-name mapping with NSS, LDAP, Kerberos realms, and optional static mappings. The sample is also included in distribution by `Makefile.am`.

Risks: most options are commented, so defaults must be kept in sync with code and man pages. LDAP examples include required-looking sample host/base values that should not be mistaken for live defaults. Multi-domain `No-Strip` behavior can alter lookup semantics significantly.

Test signals: parse every documented section, defaults when commented, Method/GSS-Methods lists, Domain omission DNS fallback, Local-Realms handling, No-Strip/Reformat-Group values, and LDAP option retrieval by plugin code.
