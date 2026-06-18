# sources/user-network-fs/impacket/examples/GetUserSPNs.py

## Purpose

`GetUserSPNs.py` enumerates Active Directory service principal names associated with user or machine accounts and optionally requests Kerberos service tickets for Kerberoasting. It can output crackable TGS hashes, save ccache files, query cross-domain targets, process user/SPN lists, and support a no-preauth roasting path.

## Important APIs, Types, and Functions

`GetUserSPNs.printTable` formats LDAP rows. `getTGT` loads an existing ccache TGT or requests one, trying NTLM-derived RC4 material unless `-no-rc4` is set. `outputTGS` decodes `TGS_REP` or `AS_REP` and formats RC4, AES128, AES256, or DES tickets for cracking, with optional ccache save. `run` performs LDAP enumeration and optional TGS requests. `request_users_file_TGSs` and `request_multiple_TGSs` support list-driven operation.

## Control Flow

The CLI parses target identity, optional target domain, stealth/machine filters, request selectors, output/save options, and authentication settings. `run` logs into LDAP for the target domain, builds a filter for enabled person accounts by default or computer accounts with `-machine-only`; unless `-stealth` is set, it adds `servicePrincipalName=*`. It requests SPN and account metadata with a paged control, filters disabled accounts, prints rows, then if `-request`, `-request-user`, or `-request-machine` is active, obtains a TGT and requests one TGS per unique account. Users-file mode bypasses LDAP and requests tickets for supplied principals.

## State and Persistence Behavior

The script performs LDAP reads and Kerberos exchanges. It may write crackable hashes to `-outputfile` and ccache files named `<username>.ccache` when `-save` is set. It reads Kerberos credential caches through `CCache.parseFile`. It does not modify AD objects.

## Dependencies and Integration Points

It depends on Impacket LDAP helpers, Kerberos TGT/TGS APIs, ccache support, pyasn1 ticket decoding, NTLM hash derivation, AD UAC/delegation flags, and hashcat/John TGS formats. Cross-domain behavior intentionally ignores custom KDC host/IP to avoid breaking referral flows.

## Risks and Edge Cases

The script outputs and saves sensitive ticket material. In normal `run`, it requests TGS using a down-level account principal rather than the original SPN from the row, which is a deliberate account-targeted path but can surprise users expecting per-SPN tickets. `-stealth` can query huge account sets and warns about memory. Output file and ccache names may overwrite existing files. Several LDAP filters use extensible-match-like `sAMAccountName:=` syntax. Time formatting is local. Broad exception handling can continue after individual ticket failures.

## Test Signals

Unit tests should cover LDAP filter construction for person, machine-only, request-user, request-machine, and stealth modes; output formatting for each encryption type; ccache save paths; TGT fallback paths; and users-file mode. Integration tests need AD/Kerberos fixtures with SPNs, delegation flags, disabled accounts, and cross-domain trust cases.
