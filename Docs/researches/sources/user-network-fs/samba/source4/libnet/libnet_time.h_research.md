# sources/user-network-fs/samba/source4/libnet/libnet_time.h

## Purpose

`libnet_time.h` declares the request/response union for retrieving remote time of day.

## Important APIs, Types, and Functions

`enum libnet_RemoteTOD_level` defines generic and SRVSVC backends. `union libnet_RemoteTOD` contains input `server_name` and output `time`, `time_zone`, and `error_string`.

## Control Flow

The level tag drives dispatch in `libnet_RemoteTOD()`. Generic requests are translated to SRVSVC requests by the implementation.

## State and Persistence Behavior

The union is transient and returns scalar values. It does not own network resources.

## Dependencies and Integration Points

It relies on C `time_t` and libnet callers. Python binding `Net.time()` consumes it and formats the returned `time_t` with local timezone formatting.

## Risks and Edge Cases

Callers must set the level and server name. Timezone interpretation needs implementation-level validation.

## Test Signals

Compile-time structure use plus runtime `libnet_RemoteTOD()` and Python `Net.time()` calls are the main signal.
