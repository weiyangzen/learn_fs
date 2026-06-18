# sources/user-network-fs/impacket/examples/getST.py

## Purpose

`getST.py` obtains Kerberos service tickets and saves them as ccache files. It supports normal TGS requests, TGT renewal, S4U2Self/S4U2Proxy constrained delegation, resource-based constrained delegation with an additional ticket, user-to-user mode in S4U flows, alternate service-name rewriting, forced forwardable-ticket modification for CVE-2020-17049 style testing, and DMSA key package extraction.

## Important APIs, Types, and Functions

`GETST.__init__()` stores credentials, hashes, AES key, KDC host, S4U flags, additional ticket path, DMSA mode, and output-name state. `saveTicket(ticket, sessionKey)` builds a `CCache` from a TGS, optionally rewrites the ticket service principal and ccache credential server when `-altservice` is used, and saves `<user-or-impersonated>@<service>.ccache`.

`doS4U2ProxyWithAdditionalTicket()` loads an existing ccache service ticket, optionally rewrites its forwardable flag by decrypting and re-encrypting the ticket, then builds an S4U2Proxy TGS-REQ with `PA_PAC_OPTIONS.resource_based_constrained_delegation`.

`doS4U()` builds S4U2Self padata using either traditional `PA_FOR_USER_ENC` HMAC-MD5 or DMSA `PA_S4U_X509_USER`, optionally requests U2U, optionally extracts `KERB_DMSA_KEY_PACKAGE`, and then either returns the S4U2Self ticket or performs S4U2Proxy. `run()` chooses cached TGT, fresh TGT, normal TGS, renew, S4U with additional ticket, or S4U without additional ticket.

## Control Flow

The CLI validates combinations: `-spn` is required unless `-self` is set, `-impersonate` is required for S4U2Self-only and additional-ticket modes, and `-altservice` in self-only mode must include service class and hostname. Identity parsing then feeds `GETST.run()`.

`run()` first tries `CCache.parseFile()` for a TGT. If none exists, it requests one with `getKerberosTGT()`. Without `-impersonate`, it calls `getKerberosTGS()` for the requested SPN or renews the TGT. With impersonation, it runs S4U logic. S4U2Proxy paths construct AP-REQ authenticators, KDC option flags, SPN principals, additional tickets, and encryption-type lists manually, then call `sendReceive()`.

## State and Persistence Behavior

The primary persistent output is a ccache file in the current directory. The script also reads existing ccaches from `KRB5CCNAME` through Impacket and reads an additional ticket ccache when requested. It mutates in-memory tickets for alternate service names and forced forwardable flags before saving or forwarding them. DMSA mode logs extracted current and previous keys.

## Dependencies and Integration Points

Dependencies include Impacket Kerberos ASN.1, ccache, crypto, NTLM hash helpers, pyasn1, and the example logger. Integration points are KDC AS/TGS exchanges, existing Kerberos credential caches, ccache consumers such as SMB/WMI tools, and AD delegation policy.

## Risks and Edge Cases

This is security-sensitive code that can print or save reusable tickets and keys. `-force-forwardable` requires correct account keys; wrong hashes/AES keys cause decrypt/re-encrypt failure. Alternate service rewriting changes ticket metadata without changing the encrypted ticket server name semantics expected by all services, so compatibility varies. Error handling catches broad exceptions and may return without a nonzero exit. DMSA handling returns early if no encrypted padata exists, which can skip ticket saving. Manual ASN.1 construction is brittle across KDC policy changes. The condition checking `options.u2u is not None` is always true for argparse booleans, so its intended validation is weaker than written.

## Test Signals

Unit tests should mock Kerberos responses and validate padata construction, KDC option flags, ccache naming, altservice rewrite cases, and parser validation. Regression tests should cover imported use, additional-ticket loading errors, `-self` without SPN, `-force-forwardable` key selection for RC4 and AES, and DMSA no-key-package behavior. Integration tests need an AD lab with normal SPN issuance, constrained delegation, RBCD, U2U, and renewal cases.
