# File Research: sources/os/linux/linux/fs/dlm/midcomms.h

## Role

`midcomms.h` declares DLM mid-level communication APIs.

## Interface

It exposes incoming buffer validation/processing, outgoing mhandle allocation/commit, address registration, version wait, node close/start/stop/init/exit/shutdown, member add/remove notifications, retransmission trigger, debug state accessors, raw message send, and cache creation.

## Research Notes

Read completely. This header is the contract between transport, recovery, member management, debugfs, and message-sending code.
