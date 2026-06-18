# Research: sources/user-network-fs/samba/source4/setup/krb5.conf

Purpose: Kerberos configuration template emitted during Samba AD provisioning.

Content and integration: it sets `default_realm` from `${REALM}`, disables DNS realm lookup, enables DNS KDC lookup, maps the realm to `${DNSDOMAIN}`, and maps `${HOSTNAME}` to `${REALM}` in `[domain_realm]`.

State and dependencies: placeholders are substituted by Samba setup/provisioning code before installation. The resulting file affects Kerberos client behavior for Samba tools and test environments.

Risks and test signals: correctness depends on consistent realm, DNS domain, and hostname substitutions. Because KDC lookup is DNS-driven, DNS setup failures can appear as Kerberos failures. Signals include successful kinit/samba-tool Kerberos tests registered by `tests.py`.
