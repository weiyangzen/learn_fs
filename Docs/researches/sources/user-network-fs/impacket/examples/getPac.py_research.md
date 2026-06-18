# sources/user-network-fs/impacket/examples/getPac.py

## Purpose

`getPac.py` obtains and prints the Privilege Attribute Certificate (PAC) for a target user using a normal authenticated account. It combines Kerberos S4U2Self with user-to-user authentication so the returned ticket can be decrypted and the PAC authorization data can be decoded.

## Important APIs, Types, and Functions

`S4U2SELF.printPac(data)` decodes an `EncTicketPart`, extracts `AD_IF_RELEVANT`, parses `PACTYPE`, walks `PAC_INFO_BUFFER` entries, and decodes known PAC buffer types including `KERB_VALIDATION_INFO`, `PAC_CLIENT_INFO`, server and KDC checksums, and UPN/DNS info. Unknown buffers are hex-dumped.

`S4U2SELF.__init__()` stores the authenticated account, domain, target user, and optional LM/NT hashes. `S4U2SELF.dump()` requests a TGT with `getKerberosTGT()`, manually builds an AP-REQ and TGS-REQ with `PA_FOR_USER_ENC`, sets `enc_tkt_in_skey`, embeds the account TGT as an additional ticket, sends the request with `sendReceive()`, decrypts the returned ticket, and passes the plaintext ticket to `printPac()`.

## Control Flow

The CLI requires credentials and `-targetUser`. It parses identity and hashes, then runs `S4U2SELF.dump()`. The Kerberos flow is hand-built with pyasn1 structures: TGT acquisition, AP-REQ authenticator encryption using key usage 7, S4U checksum computation over the target user/domain/auth package with HMAC-MD5, TGS request body construction, additional ticket inclusion for U2U, KDC request/response exchange, service ticket decryption, and PAC printing.

## State and Persistence Behavior

The script is read-only from the domain perspective and writes no ccache. It prints PAC contents to stdout and debug logs. In-memory state includes credentials, Kerberos tickets, ciphers, session keys, and decoded PAC structures.

## Dependencies and Integration Points

It depends on Impacket Kerberos ASN.1 types, crypto tables, PAC structures, `getKerberosTGT()`, `sendReceive()`, pyasn1 DER encoding/decoding, and the example logger. It integrates tightly with Kerberos KDC behavior for S4U2Self and U2U.

## Risks and Edge Cases

The script has a library-safety bug: in `dump()`, key derivation references `password` instead of `self.__password`, which works only when the module is executed as `__main__` and a global `password` variable exists. The hash/key handling is RC4-centric and has fragile type checks around `self.__nthash`. PAC parsing assumes expected authorization-data layout and buffer offsets. Because requests are manually assembled, KDC policy differences, encryption-type restrictions, protected users, and domain functional behavior can break the flow. Debug mode can print sensitive ticket and PAC material.

## Test Signals

Tests should cover PAC buffer parsing with captured tickets, unknown buffer hexdump behavior, and key selection with password versus hashes. A regression test should import `S4U2SELF` and call `dump()` with mocked Kerberos functions to catch the global `password` dependency. Integration tests need a lab KDC supporting S4U2Self/U2U and should verify expected PAC fields for a known target user.
