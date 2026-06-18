# sources/user-network-fs/samba/source3/smbd/smb1_ipc.h

## Purpose

`smb1_ipc.h` declares the public SMB1 IPC transaction functions implemented by `smb1_ipc.c`. It exposes the reply-fragmentation helper and the primary/secondary SMBtrans command handlers used by SMB1 dispatch.

## Important APIs, Types, And Functions

The header exports:

- `send_trans_reply(connection_struct *conn, struct smb_request *req, char *rparam, int rparam_len, char *rdata, int rdata_len, bool buffer_too_large);`
- `reply_trans(struct smb_request *req);`
- `reply_transs(struct smb_request *req);`

The prototypes depend on `connection_struct`, `struct smb_request`, integer lengths, and the boolean type supplied by the smbd include environment.

## Control Flow

The header itself has no executable control flow. Its contract is that SMB1 command dispatch calls `reply_trans()` for primary `SMBtrans` packets and `reply_transs()` for secondary packets. Other IPC/RPC code can use `send_trans_reply()` to emit correctly formatted SMBtrans responses, including fragmented replies and buffer-overflow/more-data signaling.

## State And Persistence Behavior

No state is owned by the header. The declared implementation may mutate request output buffers, pending transaction lists, connection/tcon state, and async request ownership. Callers must treat these functions as SMB request handlers that may send replies immediately, defer replies asynchronously, or disconnect state on close-on-completion.

## Dependencies And Integration Points

This header is the interface between SMB1 protocol dispatch and the IPC transaction implementation. It also allows named-pipe/RPC paths to share transaction response formatting without duplicating SMB1 wire-layout code.

## Risks

Because `send_trans_reply()` accepts raw parameter/data pointers and signed lengths, callers must pass valid buffers and lengths that match the negotiated transaction semantics. Misuse can produce malformed SMB1 replies. Command handlers own complex request lifetimes; dispatch code must not send additional replies after handlers defer or complete a transaction.

## Test Signals

Build tests catch prototype drift. Protocol tests should verify that dispatch reaches `reply_trans()`/`reply_transs()` for the right SMB commands and that users of `send_trans_reply()` produce correctly fragmented responses for normal and buffer-too-large cases.
