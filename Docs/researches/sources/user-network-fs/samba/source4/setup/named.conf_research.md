# Research: sources/user-network-fs/samba/source4/setup/named.conf

Purpose: BIND named configuration template for Samba AD DNS zones.

Content and integration: it defines a master forward zone for `${DNSDOMAIN}.`, stores data in `${ZONE_FILE}`, includes dynamic update policy from `${NAMED_CONF_UPDATE}`, and sets `check-names ignore` to allow AD-specific records such as `_msdcs`. It also documents an optional reverse zone and GSS-TSIG update policy considerations.

State and dependencies: placeholders are filled by provisioning. Runtime DNS updates depend on generated update-policy content and BIND support for secure updates.

Risks and test signals: wrong include paths or zone filenames break DNS startup. Removing update policies disables secure dynamic updates. Test signals come from DNS-related selftests and samba-tool DNS update tests.
