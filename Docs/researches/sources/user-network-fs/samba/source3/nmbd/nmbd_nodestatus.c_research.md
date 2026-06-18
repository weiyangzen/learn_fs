# sources/user-network-fs/samba/source3/nmbd/nmbd_nodestatus.c

## Purpose
Provides the asynchronous client-side node-status query helper. Other nmbd modules use it to ask a remote NetBIOS node for all registered names at an IP address, then parse the returned resource record in their own callbacks.

## Important APIs, Types, And Functions
Public API is `node_status()`. Internal callbacks are `node_status_response()` and `node_status_timeout_response()`. It uses `queue_node_status()`, `struct response_record`, and node-status callback typedefs from `nmbd.h`.

## Control Flow
`node_status()` queues a node-status packet to the supplied IP and returns true only on queue/send failure. `node_status_response()` validates that answer and question names match, passes the entire answer resource record and source IP to the caller's success callback, then removes the response record. `node_status_timeout_response()` invokes the caller fail callback and removes the response record.

## State And Persistence
Only transient response-record lifecycle is owned here. Callers such as browse sync update DMB names, DMB addresses, or unicast workgroups from returned records.

## Dependencies, Risks, And Test Signals
Used by browse sync for DMB IP-to-name mapping and foreign workgroup discovery. Risks are strict answer-name validation and caller-side parsing safety. Test signals include success callback delivery with unmodified answers, timeout fail callback execution, response-record removal in both paths, and queue failure returning true.
