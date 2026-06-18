# File Research: sources/os/plan9/9front/sys/src/cmd/gdbfs/dat.h

## Purpose
Declares shared state and callbacks for the `gdbfs` remote-debugging filesystem.

## Key Elements
Defines debug flag/prototype, minimum write packet size, target states, global `gdb` state with thread id, state lock, packet length, write fd, read Bio, and command channel. Declares initialization/shutdown plus memory/register/control request handlers.

## Dependencies
Requires Plan 9 thread `QLock`, Bio, and 9P `Req` types from including modules.

## Behavior/Risks
The single global `gdb` object means one remote target per filesystem instance. State transitions are guarded by the embedded `QLock`, while packet exchange is serialized through the command channel.
