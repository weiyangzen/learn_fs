# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/message.h

Public message-layer header.

It defines payload index nodes, payload handled marker `PL_MARK`, post-send hook nodes, `struct message`, and message flags for last message, encrypted state, send-queue membership, prioritized sending, authentication, NAT-T reception, and no-retransmit behavior.

It declares message construction, reply allocation, payload insertion, SA payload construction, receive/send/drop/delete/notification/info handling, raw dump, SA negotiation, message copy, post-send hook registration/execution, header setup, retransmit send callback, and first-payload lookup.
