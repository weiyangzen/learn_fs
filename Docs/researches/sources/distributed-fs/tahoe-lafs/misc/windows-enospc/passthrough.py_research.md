# sources/distributed-fs/tahoe-lafs/misc/windows-enospc/passthrough.py

## Purpose

This Windows helper passes stdin to stdout using Twisted's Windows-aware stdio machinery. It exists to avoid ENOSPC errors that can occur when writing to non-blocking pipes through Unix-like APIs on Windows.

## Important APIs, Types, And Functions

`Passthrough` implements `IHalfCloseableProtocol`. `dataReceived()` writes received bytes to the transport, `readConnectionLost()` closes output, and `writeConnectionLost()`/`connectionLost()` stop the reactor while tolerating `ReactorNotRunning`. At module import/run time, `StandardIO(Passthrough())` attaches the protocol to process stdio and `reactor.run()` starts the event loop.

## Control Flow

The module executes immediately. Twisted delivers stdin bytes to `dataReceived()`, which mirrors them to stdout. Half-close and full-close notifications shut down transport or reactor so the process exits after data transfer completes.

## State And Persistence

There is no durable state. Runtime state is Twisted reactor state and the protocol transport. The script does not buffer beyond Twisted's normal transport behavior.

## Dependencies And Integration Points

It depends on `twisted.internet.stdio.StandardIO`, `reactor`, `Protocol`, `IHalfCloseableProtocol`, `ReactorNotRunning`, and `zope.interface.implementer`. It is likely invoked as a subprocess in Windows-specific test or tooling paths.

## Risks

Because the reactor starts at import time, importing this module in tests would block. It assumes Twisted stdio is the desired pipe abstraction on the target Windows runtime. Exceptions from `transport.write()` are not translated, so unexpected transport errors propagate through Twisted logging.

## Test Signals

Exercise by piping binary and text data through the script on Windows, closing stdin early, closing stdout early, and verifying process exit without ENOSPC or hanging reactor failures.
