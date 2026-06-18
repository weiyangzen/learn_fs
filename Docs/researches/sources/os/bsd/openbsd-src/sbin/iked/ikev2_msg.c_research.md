# File Research: sources/os/bsd/openbsd-src/sbin/iked/ikev2_msg.c

Read completely: 1370 lines.

Implements iked's IKE datagram message lifecycle: UDP/NAT-T receive, IKEv1 rejection logging, outbound message construction and send, encrypted payload encryption/decryption, integrity tags, IKE_AUTH signed/MACed data generation, authentication verification/signing, encrypted fragmentation, response/request retransmit queues, and timers.

Core receive/send flow:
- `ikev2_msg_cb()` receives from a bound iked socket with `recvfromto()`, preserves local/peer addresses, strips the 4-byte NAT-T non-ESP marker when receiving on the NAT-T port, copies the datagram into an `ibuf`, initializes proposal/certreq queues, dispatches IKEv1 to `ikev1_recv()` and IKEv2 to `ikev2_recv()`, then cleans the message.
- `ikev1_recv()` only validates/logs the IKEv1 header and reports that IKEv1 is unsupported.
- `ikev2_msg_init()` prepares an `iked_message` with peer/local addresses, response flag, static max-size `ibuf`, `msg_parent` set to itself, and proposal queue initialization.
- `ikev2_msg_copy()` duplicates the payload from `msg_offset` onward for retransmission/cache queues, preserving fd, msgid, offset, and SA pointer.
- `ikev2_msg_cleanup()` frees all message-owned `ibuf`s, EAP/user strings, CP address records, proposals, certreq entries, and finally `msg_data`; for child/decrypted messages it only frees the local `msg_data`.
- `ikev2_msg_valid_ike_sa()` rejects closed SAs and permits only initiator informational requests on closing SAs, so DELETE can still be processed during shutdown.
- `ikev2_msg_send()` logs the exchange, optionally prepends the NAT-T marker, sends with `sendtofrom()`, updates send statistics, handles `EADDRNOTAVAIL` by moving the SA toward closing, and stores a retransmittable copy in either `sa_responses` or `sa_requests`.
- `ikev2_msg_id()` increments `sa_reqid` and logs overflow.

Encryption, integrity, and fragmentation:
- `ikev2_msg_encrypt_prepare()` computes final IKE/SK/SKF payload lengths before encryption so headers included in authentication are correct. It accounts for IV, padded ciphertext, integrity/tag length, and fragment header size.
- `ikev2_msg_encrypt()` pads plaintext with random bytes plus pad length, selects initiator or responder encryption key, initializes the cipher, prepends the IV, optionally supplies AAD for AEAD ciphers, appends ciphertext, reserves zeroed tag space, and consumes/frees the plaintext buffer.
- `ikev2_msg_integr()` fills the integrity/tag field. Non-AEAD uses the selected auth key and HMAC over the message excluding the tag; AEAD obtains the tag from the cipher context.
- `ikev2_msg_decrypt()` selects peer-direction keys, verifies HMAC for non-AEAD before decryption, configures AEAD tag/AAD when needed, decrypts the encrypted body, checks block alignment, strips padding and pad-length byte, and returns plaintext.
- `ikev2_check_frag_oversize()` estimates encrypted packet size against IPv4/IPv6 fragment limits and only requests fragmentation when the SA has fragmentation enabled.
- `ikev2_msg_send_encrypt()` builds a normal encrypted SK message, assigns current/next message ID, encrypts, authenticates, parses the outgoing packet for local bookkeeping, and sends it.
- `ikev2_send_encrypted_fragments()` splits a plaintext encrypted-payload body into SKF fragments sized under IPv4/IPv6 limits, uses one message ID for all fragments, emits fragment counters, encrypts/authenticates each fragment independently, sends each one, and updates fragment success/failure counters.

IKE_AUTH data and authentication:
- `ikev2_msg_auth()` constructs the RFC-style AUTH input from the first/second IKE message, opposite nonce, and PRF over the local ID buffer using the initiator or responder PRF key.
- `ikev2_msg_authverify()` verifies peer AUTH using either a PSK-derived key or the saved peer certificate/key material, drives DSA/PSK verification helpers, and transitions SA state to AUTH success or request on failure.
- `ikev2_msg_authsign()` signs/MACs local AUTH data using PSK or local certificate key material, replaces `sa_localauth.id_buf`, and records the selected auth method.

Peer/origin and sockets:
- `ikev2_msg_frompeer()` compares the packet initiator flag against the SA initiator role to decide whether a message is from the peer or locally generated/parsed.
- `ikev2_msg_getsocket()` selects the IPv4/IPv6 normal or NAT-T socket from `env`.

Retransmit queueing:
- `ikev2_msg_enqueue()` groups messages by msgid and exchange in `iked_msg_retransmit`, initializes fragment subqueues and the response/retransmit timer, and appends the fragment/message copy.
- `ikev2_msg_prevail()` drops queued older retransmit groups after a newer message prevails.
- `ikev2_msg_dispose()` and `ikev2_msg_flushqueue()` free queued fragments, timers, and queue nodes.
- `ikev2_msg_lookup()` matches a retransmit group by first fragment's msgid and exchange.
- `ikev2_msg_retransmit_response()` resends cached responses; for SKF it only retransmits when the peer retransmits fragment number one, detected via `ikev2_pld_parse_quick()`.
- `ikev2_msg_response_timeout()` expires cached responses.
- `ikev2_msg_retransmit_timeout()` resends all cached request fragments with exponential backoff until `IKED_RETRANSMIT_TRIES`, then records the limit and frees the SA.

Risks and notes:
- Message ownership depends heavily on `msg_parent`; cleanup of decrypted child messages intentionally differs from top-level messages.
- AEAD support is split across encryption/decryption/integrity: AAD and tag state must be set before final/tag retrieval.
- Fragment retransmission assumes the first fragment is sufficient to trigger response resend.
- A retransmit send failure frees the SA immediately after setting a reason.
