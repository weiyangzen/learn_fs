# sources/user-network-fs/impacket/examples/kintercept.py

## Purpose

`kintercept.py` is a TCP interception proxy aimed at Kerberos KDC traffic. It can transparently forward streams or modify Kerberos TGS requests/replies for S4U testing, especially PA-FOR-USER unkeyed checksum cases related to CVE-2018-16860 and CVE-2019-0734.

## Important APIs, Types, and Functions

`process_s4u2else_req(data, impostor)` decodes a `TGS_REQ`, finds `PA_TGS_REQ` and `PA_FOR_USER`, changes the PA-FOR-USER user name to an impostor, recalculates a CRC32 checksum, and returns a re-encoded request. `mod_tgs_rep_user(data, reply_user)` decodes a `TGS_REP` and rewrites the cname.

`InterceptConn` is an `asyncore.dispatcher` that pairs with a peer connection, buffers outbound data, handles half-closed sockets, and forwards bytes. `InterceptKRB5Tcp(process_record_func, arg)` returns a subclass that parses Kerberos TCP record framing and applies a record transformer. `InterceptConnFactory` maps handler names to connection classes. `InterceptServer` listens locally, connects upstream, pairs downstream/upstream dispatchers, and enters `asyncore.loop()`.

## Control Flow

The CLI accepts upstream server/port, local listen address/port, optional request handler, and optional reply handler. On accept, the server creates a downstream connection class and upstream connection class from the factories, links them as peers, and connects upstream to the target KDC. Plain connections forward byte buffers. Kerberos-aware connections accumulate record data, parse the 4-byte big-endian length prefix, transform complete records when possible, rebuild the length prefix, and forward modified or original records.

## State and Persistence Behavior

No filesystem state is used. Each connection pair maintains buffers, EOF flags, socket state, and for Kerberos-aware connections a protocol buffer. The tool can alter live Kerberos messages in transit but does not persist tickets or keys.

## Dependencies and Integration Points

It depends on deprecated Python `asyncore`, sockets, pyasn1 DER handling, Impacket Kerberos ASN.1 structures, principals, constants, and logger setup. It integrates externally with port forwarding, firewall redirection, or client configuration that routes KDC TCP traffic through the local listener.

## Risks and Edge Cases

The code has Python 3 bytes/str hazards: it uses `''.join(reversed(str(self.proto_buffer[:4])))` and string concatenation around binary headers/messages, which can corrupt framing or raise type errors. The CRC32 S4U byte array also mixes `impostor` with strings. Handler argument parsing assumes exactly `HANDLER:ARG`. Unknown handler names return `None`, causing failures when called. `asyncore` is deprecated, and the proxy handles only TCP framing, not UDP Kerberos. Message rewriting is intentionally security-sensitive and can invalidate checksums for modern KDCs.

## Test Signals

Tests should feed captured Kerberos TCP records through the returned `InterceptKRB5Tcp` class and assert framing, transformed cname/userName, and fallback forwarding for non-TGS records. Python 3 tests should specifically catch bytes/str failures. Integration tests can run the proxy in front of a lab KDC and verify normal forwarding, request-handler modification, reply-handler modification, partial-record buffering, and half-close behavior.
