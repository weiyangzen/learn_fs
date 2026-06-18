<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wrepl/winsrepl.c -->
# sources/user-network-fs/samba/source4/libcli/wrepl/winsrepl.c

Purpose: implements the low-level WINS replication client transport and core replication requests.

Important APIs and types: `struct wrepl_socket`, `wrepl_socket_init`, `wrepl_socket_is_connected`, `wrepl_socket_donate_stream`, `wrepl_socket_split_stream`, `wrepl_best_ip`, `wrepl_connect_send`/`recv`/sync, `wrepl_request_send`/`recv`/sync, `wrepl_associate`, `wrepl_associate_stop`, `wrepl_pull_table`, and `wrepl_pull_names`. It depends on tevent queues, `tstream`, tsocket addresses, NDR WINSREPL push/pull, loadparm interface selection, and packet framing.

Control flow: operations are serialized on `request_queue`. Connect creates local and remote IPv4 socket addresses and opens a TCP stream to `WINS_REPLICATION_PORT`. Generic request marshals a `wrepl_packet` into a wrapped NDR blob, writes it to the stream, optionally disconnects or completes send-only, otherwise reads a length-prefixed PDU and unmarshals a reply. Higher-level calls build protocol packets for association start/stop, partner-table query, and owner-name pull, then validate reply message and command types.

State and persistence: `wrepl_socket` owns the event context, request timeout, queue, and active stream. Donate/split transfer stream ownership. Pull-name output converts wire names into stable `struct wrepl_name` arrays with owner/address strings. No local durable storage is written, but remote association state is created/stopped.

Risks: event context mismatch currently calls `smb_panic`, so misuse is process-fatal. Any request error frees the stream, affecting queued/future calls. The PDU parser trusts NDR length framing after a 4-byte initial read. Test signals include connect timeout, queue serialization, send-only disconnect, invalid message type handling, multi-address name conversion, stream donate/split with in-use queue, and connection teardown on read/write errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wrepl/winsrepl.c -->
