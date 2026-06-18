# sources/user-network-fs/libsmb2/lib/socket.c

## Purpose
Implements libsmb2 nonblocking socket transport, event selection, credit-gated writes, receive-state parsing, SMB3 transform handling, async connect with Happy Eyeballs behavior, server listen/accept helpers, and event callback updates.

## Important APIs, Types, And Functions
Public APIs include `smb2_which_events`, `smb2_get_fd`, `smb2_get_fds`, `smb2_write_to_socket`, `smb2_read_from_buf`, `smb2_service_fd`, `smb2_service`, `smb2_connect_async`, `smb2_bind_and_listen`, `smb2_accept_connection_async`, and `smb2_change_events`. Important internal helpers include `smb2_read_data`, `smb2_read_from_socket`, `smb2_readv_from_socket`, `smb2_readv_from_buf`, `connect_async_ai`, `smb2_connect_async_next_addr`, `interleave_addrinfo`, and fd cleanup helpers.

## Control Flow
Writes are gated by available credits, flatten compound PDU iovecs or encrypted transform buffers behind a 4-byte SPL prefix, handle partial `writev`, then move sent client PDUs to the waitqueue or free server replies. Reads use a state machine: SPL, SMB2 header, fixed payload, variable payload, padding, transform payload, or unknown reply. Header parsing updates credits, validates request/reply direction, matches client replies by message id, creates notification PDUs for oplock breaks, and invokes command-specific fixed/variable parsers. Encrypted transform frames are detected by magic, read as a transform header plus payload, decrypted by `smb3_decrypt_pdu`, and parsed from memory. Connection setup resolves host/port, interleaves address families, opens nonblocking sockets, races connection attempts with a 100 ms timeout, and promotes the first successful fd.

## State And Persistence
Major state lives in `struct smb2_context`: `fd`, connecting fd array, addrinfo cursor, outqueue, waitqueue, credits, receive iovectors, `recv_state`, SPL, current PDU, encrypted buffer cursor, callbacks, and event mask. Sent client PDUs persist in the waitqueue until matched replies arrive. Server-mode requests are queued to correlate later replies.

## Dependencies And Integration Points
This file is the transport core for all command files. It integrates signing verification through `smb2_calc_signature`, sealing through `smb3_decrypt_pdu`, PDU allocation/lookup/free, command payload dispatch, timeout handling, fd-change/event callbacks, POSIX/Windows socket APIs, and address resolution.

## Risks
The receive state machine is complex and sensitive to length arithmetic, chained PDU padding, and encrypted-vs-plain SPL accounting. Unknown replies are skipped only below a max-size guard. Signature checking mutates the received signature field while recalculating and then compares restored bytes, so regression tests are important. Happy Eyeballs fd arrays assume capacity from initial addrinfo count and require cleanup on all paths. Some error strings include stale `smb2_get_error` text rather than `strerror`.

## Test Signals
Use integration tests for partial reads/writes, credit exhaustion/refill, compound request/reply order, pending replies, unknown replies, oplock notifications, signed tamper detection, encrypted transform PDUs, IPv4/IPv6 racing, connect failure fallback, server accept, timeout processing, and event mask transitions.
