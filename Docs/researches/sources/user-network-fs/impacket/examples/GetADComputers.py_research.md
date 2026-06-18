# sources/user-network-fs/impacket/examples/GetADComputers.py

## Purpose

`GetADComputers.py` queries Active Directory LDAP for computer accounts and prints `sAMAccountName`, DNS hostname, operating system version, operating system, and optionally resolved IP address.

## Important APIs, Types, and Functions

`GetADComputers.__init__` stores credentials, Kerberos/hash options, DC settings, request filters, `-resolveIP`, base DN, and fixed table formatting. `processRecord` extracts attributes from `ldapasn1.SearchResultEntry` records and optionally resolves `dNSHostName` A records through the DC. `run` logs into LDAP with `ldap_login`, creates a paged results control, and performs the computer search.

## Control Flow

The CLI parses `domain[/username[:password]]`, authentication, DC, and `-resolveIP` options. After identity parsing and logger initialization, `run` connects to LDAP, prints the header, builds `(&(objectCategory=computer)(objectClass=computer))`, and searches with attributes `sAMAccountName`, `dNSHostName`, `operatingSystem`, and `operatingSystemVersion`. For each result, `processRecord` decodes LDAP attributes, optionally points dnspython at the DC IP and resolves hostnames, and prints a fixed-width row.

## State and Persistence Behavior

The script is read-only against LDAP and DNS. It keeps credentials and output formatting in memory. It does not write files or modify AD state.

## Dependencies and Integration Points

It depends on Impacket LDAP helpers, SAMR constants for imported but unused account flags, `dnspython` for optional hostname resolution, and Active Directory LDAP schema attributes. It integrates with Kerberos/NTLM login flow through `parse_identity` and `ldap_login`.

## Risks and Edge Cases

`-user` is stored but not used in the LDAP filter. DNS resolution is configured by mutating `dns.resolver.default_resolver`, which can affect later resolver calls in the process. Broad `except` around DNS failures hides resolver issues. Fixed-width columns truncate or misalign long names visually. Attribute decoding assumes at least one value. The search uses paged control, but per-record processing and printing are synchronous.

## Test Signals

Tests should mock LDAP entries with missing, empty, and long attributes; verify filter construction; exercise `-resolveIP` success and failure; and ensure Kerberos/hash/DC options are passed to `ldap_login`. Integration tests require an AD fixture with computer objects.
