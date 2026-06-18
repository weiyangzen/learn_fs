<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/named.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/named.conf

Purpose: BIND flat-file DNS configuration fixture from an old alpha13 Samba provision.

Important APIs/types/functions: forward zone `alpha13.samba.corp.`, zone file path, `named.conf.update` include, `check-names ignore`, and commented reverse-zone example.

Control flow: static BIND include config defines a master zone with dynamic update policy included from Samba-generated content.

State and persistence behavior: no executable code; represents historical DNS configuration state.

Dependencies and integration points: used by provision upgrade tests that migrate old BIND flat-file DNS setups.

Risks: absolute paths are fixture-specific. Comments reference old BIND GSS-TSIG behavior and optional reverse-zone setup.

Test signals: upgrade fixtures can detect/migrate this file and validate generated AD DNS/BIND DLZ replacements.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/named.conf -->
