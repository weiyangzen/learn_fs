# sources/user-network-fs/samba/source4/smb_server/smb2/keepalive.c

## Purpose
This file implements SMB2 KEEPALIVE/ECHO-style request handling. It validates the minimal fixed body, currently performs no connection-side bookkeeping, and returns a four-byte SMB2 response unless the caller requested no reply.

## Important APIs, Types, And Functions
The public entry point is `smb2srv_keepalive_recv`. `smb2srv_keepalive_backend` returns `NT_STATUS_OK` and is explicitly marked for future connection-flag updates. `smb2srv_keepalive_send` serializes the response or converts backend errors into SMB2 error replies.

## Control Flow
The receive path requires `req->in.body_size == 0x04` and the first body word equal to `0x04`. Invalid values produce `NT_STATUS_INVALID_PARAMETER`. On success, it records the backend status in `req->status`; if `SMB2SRV_REQ_CTRL_FLAG_NOT_REPLY` is set, it frees the request, otherwise it emits a fixed-size response with a zero reserved word.

## State And Persistence
The only state mutation is `req->status`. Unlike the dispatcher, this file does not update last-request timestamps, idle timers, or negotiated connection state. There is no persistence.

## Dependencies And Integration Points
It depends on SMB2 reply setup and error helpers from the SMB2 server layer. `receive.c` dispatches `SMB2_OP_KEEPALIVE` here without requiring a valid session or tcon.

## Risks And Test Signals
Risks are small but protocol-sensitive: accepting wrong body sizes would mask malformed clients, while not updating connection liveness may matter if future idle tracking expects this command. Tests should send valid keepalive packets, wrong fixed-size values, truncated bodies, no-reply internal requests, and keepalives before session setup.
