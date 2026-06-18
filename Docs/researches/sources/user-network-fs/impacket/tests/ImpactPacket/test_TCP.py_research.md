# sources/user-network-fs/impacket/tests/ImpactPacket/test_TCP.py

## Purpose

`test_TCP.py` validates TCP header parsing, serialization, setters, and flag manipulation for a fixed SYN packet with options.

## Important APIs, Types, And Functions

It imports `unittest` and `TCP`. `TestTCP.setUp()` parses a byte fixture. Tests `test_01()` through `test_09()` cover packet round-trip, getters, port setters, offset setter behavior, window/checksum setters, flag setters, `reset_flags()`, and `set_flags()`.

## Control Flow

Each test mutates the parsed TCP object and verifies getters. The offset test confirms `set_th_off()` does not disturb flags. Flag tests verify bit behavior for SYN, FIN, ACK, RST, PSH, URG, ECE, and CWR.

## State And Persistence Behavior

State is a per-test TCP object. There is no persistence or network behavior.

## Dependencies And Integration Points

The file exercises `ImpactPacket.TCP` parsing of options-bearing headers, header length fields, flag bits, and serialization.

## Risks And Edge Cases

It does not validate sequence/ack numbers, urgent pointer, option content, checksum calculation, payload handling, invalid header lengths, or malformed option lengths.

## Test Signals

Passing tests signal that common TCP header fields and flag manipulation remain stable for an options-bearing packet.
