# sources/user-network-fs/samba/source3/nmbd/nmbd_responserecordsdb.c

## Purpose
`nmbd_responserecordsdb.c` owns the in-memory database of expected responses for outbound NetBIOS name-service operations. It creates, stores, finds, and removes `response_record` entries attached to subnet records.

## Important APIs, types, and functions
- `make_response_record` allocates and initializes a response record from a sent packet and callbacks.
- `remove_response_record` safely removes a record, frees userdata, unlocks/frees the held packet, and decrements `num_response_packets`.
- `find_response_record` searches broadcast, unicast, and WINS server subnet response lists.
- `is_refresh_already_queued` detects duplicate queued refreshes.

## Control flow
Packet senders call `make_response_record` after successful transmission. The record stores transaction id, callbacks, optional copied userdata, retry timing, and a locked sent packet. Inbound responses call `find_response_record`; timeout handling later retries or removes the record.

## State and persistence behavior
All state is process-local under `subnet_record->responselist`. Records own copied userdata and locked packets. `remove_response_record` first searches the list to tolerate duplicate removal attempts. There is no disk persistence.

## Dependencies and integration points
The file depends on `nmbd.h`, list macros, packet free helpers, subnet iteration, and callback typedefs. It is used by packet queuing, name registration/query/release, WINS proxy, and WINS conflict-query logic.

## Risks and edge cases
Custom userdata copy/free callbacks can leak or incorrectly free nested packets. Transaction ids are 16-bit. `num_response_packets` must stay balanced or the main loop chooses poor poll intervals. Duplicate-remove tolerance can mask ownership bugs.

## Test signals
Tests should validate response matching, timeout removal, retry cancellation after response, duplicate remove safety, userdata deep-copy/free behavior, and refresh de-duplication.
