# File Research: sources/os/linux/linux-stable/fs/smb/client/transport.c

## Summary
Implements core SMB client transport mechanics: MID lifecycle, socket/RDMA send paths, credit waiting and reservation, synchronous and asynchronous request dispatch, compound request handling, channel selection for multichannel sessions, cancellation, response waiting, and read-response receive/discard logic.

## Main Responsibilities
- Manage MID completion and release through `cifs_wake_up_task()`, `__release_mid()`, `delete_mid()`, `cifs_sync_mid_result()`, and compound callbacks.
- Send SMB request vectors over TCP or SMB Direct RDMA via `smb_send_kvec()`, `__smb_send_rqst()`, and `smb_send_rqst()`.
- Add RFC1002 length markers, cork/uncork TCP sockets, mask signals during sends, detect partial sends, and force reconnect when a partial frame may corrupt stream framing.
- Support compressed and encrypted/transform sends by invoking compression helpers or dialect `init_transform_rq`.
- Gate requests on SMB credits with `wait_for_free_credits()`, `wait_for_free_request()`, and `wait_for_compound_request()`.
- Dispatch asynchronous requests through `cifs_call_async()` and synchronous/compound requests through `compound_send_recv()` and `cifs_send_recv()`.
- Pick an eligible multichannel server with `cifs_pick_channel()`, preferring the least loaded non-reconnecting channel.
- Receive large read responses into netfs iterators with `cifs_readv_receive()`, including malformed-response detection and discard handling.
- Discard unread frame bytes after errors with `cifs_discard_remaining_data()`, `__cifs_readv_discard()`, and `cifs_readv_discard()`.

## Control Flow
Sends reserve credits, validate the reconnect instance, allocate/setup MID entries, place MIDs on `pending_mid_q`, serialize signing/send work under the server lock, send request vectors, and wait for response state transitions. Compound sends allocate one MID per request part, use callbacks on each part to collect credits, wake the caller from the last response, update SMB3.1.1 preauth hashes during negotiate/session setup, and transfer response buffers to callers when requested.

Read receive validates the header, handles session-expired and status-pending responses, maps server errors, checks data offset/length against the frame size, reads data into the request iterator or accounts for RDMA memory registration, discards trailing bytes, dequeues the MID, and transfers `server->smallbuf` ownership to the MID.

## State And Synchronization
Uses `server->req_lock` for credits and in-flight counters, `server->srv_lock` for TCP status, `server->mid_queue_lock` for pending MID queues, per-MID locks for cancellation state, `server` send lock for serialized signing/socket send, and `ses->chan_lock` for channel selection. Correctness depends on matching credit ownership to reconnect instances and ensuring MIDs are not freed while demultiplex or callback paths can still see them.

## Risks
High-risk areas are partial TCP sends, signal interruption after partial frames, reconnect-instance races after credit reservation, compound cancellation, response-buffer ownership transfer, and read-response length/offset validation. Credit starvation logic intentionally reserves compound capacity; mistakes can cause deadlocks, request storms, or underutilization.
