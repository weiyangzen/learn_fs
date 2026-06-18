# sources/user-network-fs/impacket/tests/ImpactPacket/test_TCP_bug_issue7.py

## Purpose

`test_TCP_bug_issue7.py` is a regression test ensuring TCP option parsing does not hang when an option advertises an invalid zero length.

## Important APIs, Types, And Functions

It imports `unittest`, `Thread`, `TCP`, and `ImpactPacketException`. `TestTCP.test_01()` defines a worker thread that parses a malformed TCP header.

## Control Flow

The worker thread constructs `TCP(frame)` and accepts the expected `ImpactPacketException` message. The main test starts the daemon thread, joins for one second, and asserts it exited.

## State And Persistence Behavior

State is local thread execution and a malformed frame literal. There is no persistence.

## Dependencies And Integration Points

It exercises `ImpactPacket.TCP` option parsing and `ImpactPacketException` behavior under malformed input.

## Risks And Edge Cases

The frame is a string rather than bytes, and unexpected non-`ImpactPacketException` exceptions are ignored. The test primarily detects hangs, not all parser regressions. The one-second timeout can be noisy on overloaded hosts.

## Test Signals

Passing this test signals that zero-length TCP options terminate quickly instead of hanging.
