# sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_tdos.c

## Purpose

`ft_scanner_tdos.c` implements the forest-trust scanner. It finds inbound forest-transitive trustedDomain objects, connects to a GC-capable DC in each trusted forest, reads the remote forest's crossRef domain list, and updates the local `msDS-TrustForestTrustInfo` blob with `FOREST_TRUST_SCANNER_INFO` records for discovered domains.

## Important APIs, Types, and Functions

- `struct ft_scanner_scann_forest_state` is the async per-forest state: target TDO, discovery data, LDAP connection, TLS/GENSEC settings, partitions DN, and discovered domain array.
- `ft_scanner_scann_forest_send()` starts the async chain by selecting LDAP wrapping mode, setting DC discovery requirements, and calling `finddcs_cldap_send()`.
- The callback chain is `found_dc -> tcp_connected -> optional starttls -> optional tls_connect -> gensec_bind -> rootDSE config search -> partitions container search -> crossRef search -> done`.
- `ft_scanner_scann_forest_recv()` returns the discovered `ForestTrustDataDomainInfo` array.
- `struct ft_scanner_check_trusts_state` and `struct ft_scanner_check_trusts_domain` track all outstanding forest scans for one periodic run.
- `ft_scanner_check_trusts()` searches all TDOs and launches scans for inbound forest-transitive trusts with a bounded end time.
- `ft_scanner_check_trusts_scanned()` receives scan results, revalidates the TDO inside a transaction, updates scanner-info records, and frees the shared run state when all scans complete.

## Control Flow

`ft_scanner_check_trusts()` reads trust attributes via `dsdb_trust_search_tdos()`, parses each TDO, filters to inbound forest-transitive trusts, and starts one async scan per qualifying TDO. The timeout is usually `periodic.interval - 15` when the interval is above 75 seconds, otherwise the full interval.

The scan chain discovers a remote DC with LDAP, DS, and GC flags. It builds a target principal `ldap/<dc>/<domain>@<UPPERDOMAIN>`, creates an address using the discovered IP and port 389 or 636, opens TCP, constructs a tldap context, optionally performs StartTLS or LDAPS based on client LDAP SASL wrapping settings, and binds with system credentials using `tldap_gensec_bind_send()`. With the LDAP session established, it reads `configurationNamingContext` from rootDSE, searches `CN=Partitions` for the crossRef container, then searches child `crossRef` objects whose `systemFlags` indicate domain NCs. It extracts `dnsRoot` and `nETBIOSName` into an array and disconnects.

On completion, the callback starts an LDB transaction and re-searches the TDO by original object GUID. It verifies the SID, DNS name, NetBIOS name, inbound direction, and forest-transitive attribute still match. It parses existing forest trust info or creates the default TLN/domain-info blob. It removes stale scanner-info records not present in the latest remote scan, appends missing scanner-info records with current timestamp, NDR-encodes the updated `ForestTrustInfo`, replaces `msDS-TrustForestTrustInfo`, and commits. If nothing changed, it cancels the transaction.

## State and Persistence Behavior

Persistent state is the trustedDomain object's `msDS-TrustForestTrustInfo` attribute. Scanner-info records are derived cache entries and can be removed if no longer found remotely. The code is careful to re-read by GUID and revalidate TDO identity before modifying to avoid acting on stale async state. Transaction boundaries protect each trust blob update. Async state is talloc-owned by the periodic run and is released after the last outstanding scan callback clears its domain's `state` pointer.

## Dependencies and Integration Points

The file integrates with trust helpers from `util_trusts.c`, CLDAP DC discovery, tstream sockets, tldap, TLS parameter loading, GENSEC bind, loadparm LDAP wrapping policy, generated DRS forest trust NDR structures, and local samdb transactions. It is invoked only through the ft_scanner periodic service.

## Risks

This is network and security sensitive. TLS/wrapping configuration determines whether LDAP signing/sealing or TLS protects remote queries. Remote responses are minimally validated: current code reads DNS and NetBIOS names but not SIDs from remote crossRefs, while equality checks for scanner-info include SID, so additions may carry zero/default SID values. Availability failures are intentionally logged and retried later, not fatal. Concurrent TDO changes are handled by revalidation, but modifications by other writers after the transaction starts may still require normal LDB conflict handling. The function name contains `scann`, which is cosmetic but visible in symbols.

## Test Signals

Tests should exercise DC discovery failure, missing PDC DNS name, TCP/TLS/StartTLS/GENSEC failures, rootDSE shape errors, empty partitions result, malformed crossRef attributes, timeout behavior, no-trust/no-forest-trust fast paths, TDO mutation between launch and callback, default forest info creation, stale scanner-info removal, missing scanner-info addition, no-op update cancellation, and transaction commit/cancel behavior.
