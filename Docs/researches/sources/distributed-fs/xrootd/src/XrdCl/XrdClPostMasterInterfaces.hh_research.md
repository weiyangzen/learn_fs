# sources/distributed-fs/xrootd/src/XrdCl/XrdClPostMasterInterfaces.hh

## Purpose

This header defines the interfaces between channels, message handlers, and protocol transports. It is the core contract that lets PostMaster and Channel code handle XRootD and other transports uniformly.

## Important APIs, Types, And Functions

`MsgHandler` declares action flags (`Ignore`, `RemoveHandler`, `Raw`, `NoProcess`, `Corrupted`, `More`, etc.), stream events, message examination, status inspection, SID access, processing, optional raw body read/write hooks, stream-event handling, send-status notification, ready/waiting send hooks, raw-write detection, and expiration.

`ChannelEventHandler` receives channel events and returns whether it remains registered. `HandShakeData` carries handshake messages, URL, substream, start time, server address, client/stream names. `PathID` identifies upstream/downstream stream choices. Query structs define transport, XRootD, and stream query IDs. `TransportHandler` declares transport operations for parsing messages, initializing/finalizing channel data, handshaking, stream health, multiplexing, disconnect cleanup, queries, stream actions, sent/received notifications, encryption, signatures, file-instance count, and bind preferences.

## Control Flow

Channels use `TransportHandler` to initialize protocol-specific channel data, perform per-stream handshakes, choose streams for outbound messages, parse inbound headers/bodies, and react to received control messages. Incoming messages are offered to `MsgHandler::Examine`; handler action bits drive whether the message is ignored, processed, read raw, or causes handler removal/disconnect. Channel event handlers observe stream readiness/failure independently from request handlers.

## State And Persistence Behavior

This header declares contracts only. State is carried through `AnyObject &channelData`, `HandShakeData`, messages, and handler implementations. No persistence is defined.

## Dependencies And Integration Points

The file depends on XrdCl response/status types, `AnyObject`, `URL`, `Message`, `Socket`, and `XrdNetAddr`. It is implemented by XRootD transport code and consumed by `Channel`, `PostMaster`, request handlers, and redirect handling.

## Risks And Edge Cases

Action flags are bitmasks, so combinations must be handled consistently by channel code. Raw read/write hooks bypass normal message body buffering and must only return socket-related errors. `TransportHandler` owns a large, stateful protocol contract; incomplete implementations can break reconnect, multiplexing, encryption, or request matching. Query ID ranges have comments that appear inconsistent for stream IDs, so extension authors should check existing usage.

## Test Signals

Transport conformance tests should exercise partial header/body reads with retry, handshake progress/failure, stream TTL/broken detection, multiplex and substream hints, raw handler reads/writes, action flag combinations, encryption decision paths, and query responses for transport name/auth/protocol/encryption and stream address values.
