# sources/user-network-fs/impacket/impacket/nmb.py

## Purpose
`nmb.py` implements NetBIOS name service helpers and NetBIOS session service framing used by Impacket's SMB stack and related examples. It handles RFC 1001/1002 name encoding/decoding, NBNS query/registration/status packet structures over UDP port 137, NetBIOS session packet framing over TCP port 139, direct SMB session use over TCP port 445, and NetBIOS datagram framing over UDP port 138.

## Important APIs, Types, and Functions
The module defines constants for NetBIOS name-service ports, SMB direct-hosting port, node/name types, opcodes, NBNS flags, question/resource-record types, response codes, name flags, NetBIOS session packet types, and `NAME_TYPES` display text.

`encode_name(name, nametype, scope)` and `decode_name(name)` implement first- and second-level NetBIOS name encoding. `_do_first_level_encoding()` and `_do_first_level_decoding()` are regex callbacks. `NetBIOSError` and `NetBIOSTimeout` are the module's error types.

The `Structure` packet classes model NBNS payloads: `NBNSResourceRecord`, `NBNodeStatusResponse`, `NBPositiveNameQueryResponse`, `NAME_SERVICE_PACKET`, `QUESTION_ENTRY`, `RESOURCE_RECORD`, `NAME_REGISTRATION_REQUEST`, `NAME_OVERWRITE_REQUEST`, `NAME_REFRESH_REQUEST`, `NAME_REGISTRATION_RESPONSE`, `NAME_CONFLICT_DEMAND`, `NAME_QUERY_REQUEST`, `ADDR_ENTRY`, `NODE_STATUS_REQUEST`, `NODE_NAME_ENTRY`, and `STATISTICS`.

`NetBIOS` is the high-level NBNS client. It exposes nameserver/broadcast setters and getters, `gethostbyname()`, `getnodestatus()`, `getnetbiosname()`, `getmacaddress()`, `name_registration_request()`, `name_query_request()`, and `node_status_request()`.

The session-service classes are `NetBIOSSessionPacket`, abstract `NetBIOSSession`, `NetBIOSUDPSessionPacket`, `NetBIOSUDPSession`, and `NetBIOSTCPSession`. `NetBIOSTCPSession` is the important SMB-facing class, with `send_packet()`, `recv_packet()`, `_request_session()`, `polling_read()`, `non_polling_read()`, and private `__read()` for exact-length reads.

## Control Flow
NBNS name lookup starts by encoding a NetBIOS name, filling a request structure with a random transaction ID, and calling `NetBIOS.send()`. `_setup_connection()` opens a UDP socket bound to a random high source port and enables broadcast. `send()` sends the packet to the configured destination, waits with `select.select()`, retries up to three times on timeout, parses a `NAME_SERVICE_PACKET`, validates the transaction ID, raises `NetBIOSError` for negative response codes, and returns the response. `name_query_request()` wraps successful responses in `NBPositiveNameQueryResponse`. `node_status_request()` wraps the answer in `NBNodeStatusResponse`, updates the cached MAC address, and returns the parsed node-name entries.

`NetBIOSSession.__init__()` normalizes local and remote names to 15 uppercase characters, handles the special `*SMBSERVER` name by substituting the IP address for direct port 445 or trying an NBNS node-status lookup for port 139, opens or adopts a socket, and requests a NetBIOS session only when connecting to port 139. `NetBIOSTCPSession._request_session()` sends a session request containing encoded remote and local names, then waits for positive or negative session responses while ignoring keepalives and unrelated session messages.

TCP `send_packet()` wraps upper-layer data in a `NETBIOS_SESSION_MESSAGE` header. `recv_packet()` reads an exact packet, recursively discards keepalives, and returns a `NetBIOSSessionPacket`. `__read()` first reads the four-byte session header, computes 17-bit session-message lengths from the flags byte when needed, then reads the indicated payload length using either `polling_read()` or `non_polling_read()`.

UDP session sends build `NetBIOSUDPSessionPacket` datagrams with source/destination encoded names and data payload, send to the connected peer, close and reopen the UDP socket, and receive only packets whose peer tuple matches the configured remote endpoint.

## State and Persistence Behavior
`NetBIOS` stores the configured name-service port, optional nameserver, broadcast address, cached socket during a send, and the last node-status MAC address. Requests use transaction IDs from `random.SystemRandom()` when available. No filesystem persistence occurs.

`NetBIOSSession` stores normalized local/remote names, local/remote types, remote host, and the active socket. `NetBIOSUDPSession` also tracks a peer tuple and monotonically incremented datagram ID. `NetBIOSTCPSession` stores whether select polling is used and selects a read function at construction. Sockets are closed only through explicit `close()` or by UDP send's close/reopen behavior; TCP receive timeouts temporarily mutate the socket timeout during reads.

## Dependencies and Integration Points
The module depends on `errno`, `re`, `select`, `socket`, `string`, `time`, `random`, `struct.pack/unpack`, `six` helpers, and Impacket `Structure`. It is central to SMB integration: `impacket/smb.py`, `impacket/smb3.py`, and `impacket/smbconnection.py` instantiate `NetBIOSTCPSession`; `smbserver.py` and ntlmrelayx SOCKS SMB plugins also use it. Examples such as `DumpNTLMInfo.py` use NetBIOS sessions directly. Tests in `tests/SMB_RPC/test_nmb.py` cover name encode/decode, local mocked NBNS parsing, and remote NBNS operations.

## Risks and Edge Cases
`encode_name()` and `decode_name()` are old compatibility code. Scope decoding appears flawed because `decoded_domain` is overwritten rather than appended for multiple labels, and the remote tests include a TODO to fix scope functionality. `decode_name()` uses `assert name_length == 32`, so optimized Python mode would remove that validation and invalid data could fail later.

`NetBIOS._setup_connection()` initializes `has_bind = 1`, so the final `Cannot bind` branch is effectively unreachable even if all bind attempts fail; the socket may continue without a successful explicit bind. It also does not break after a successful bind. `send()` closes the UDP socket only after a matching response; repeated mismatched responses can keep looping until timeout/retry behavior exits. Negative responses are decoded only from the low four bits of `FLAGS`.

`NBNodeStatusResponse.rawData()` builds `res` but does not return it. `NetBIOSError.get_error_code()` returns `self.error`, which is never assigned; callers should use `error_code` directly or this should be fixed. Some exception handlers assume `ex.errno` exists for arbitrary exceptions. `NetBIOSUDPSession._setup_connection()` creates and connects a UDP socket, then immediately replaces it with a second socket, wasting the first. UDP session send uses `str(p)`, another Python-2-style byte/string risk.

TCP exact-length reads are robust in intent but can block up to a one-hour default when timeout is `None`. `recv_packet()` recursively discards keepalives, which is fine for normal traffic but could recurse repeatedly on a pathological stream. Direct-hosted SMB on port 445 skips the NetBIOS session request but still uses session-message framing, as expected by Impacket SMB.

## Test Signals
Existing tests already exercise encode/decode truncation, mocked node status parsing, mocked name lookup parsing, and remote NBNS flows. Additional focused tests should cover scoped names with multiple labels, invalid encoded-name length, `NetBIOSError.get_error_code()`, `NBNodeStatusResponse.rawData()` return behavior, bind failure in `_setup_connection()`, timeout/retry accounting in `NetBIOS.send()`, transaction-ID mismatch handling, TCP session length parsing above 65535 bytes, keepalive discard, and Python 3 byte output for UDP/TCP packet sends. Integration tests should keep covering SMB1/SMB2/SMB3 use through `NetBIOSTCPSession` on ports 139 and 445.
