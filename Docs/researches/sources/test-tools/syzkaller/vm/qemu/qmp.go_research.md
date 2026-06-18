# sources/test-tools/syzkaller/vm/qemu/qmp.go

## Purpose

`qmp.go` implements QEMU Machine Protocol support used by the QEMU backend for monitor commands and HMP passthrough diagnostics.

## Important APIs, Types, and Functions

Types are `qmpVersion`, `qmpBanner`, `qmpCommand`, `hmpCommand`, and `qmpResponse`. Methods are `qmpConnCheck`, `qmpRecv`, `doQmp`, `qmp`, and `hmp`.

## Control Flow

`qmpConnCheck` lazily dials the monitor TCP port, decodes the QMP banner, initializes JSON encoder/decoder, sends `qmp_capabilities`, and stores the connection. `qmpRecv` skips asynchronous event messages until it gets a command response. `qmp` sends a command, validates error/return fields, and treats HMP textual `Error:` or `unknown command:` replies as errors. `hmp` wraps a human monitor command in `human-monitor-command` with CPU index and returns the string output.

## State and Persistence Behavior

The monitor connection, encoder, and decoder are stored on the QEMU instance and reused. No external state is persisted beyond QEMU monitor side effects from commands.

## Dependencies and Integration Points

It depends on `net`, `encoding/json`, QEMU QMP/HMP protocols, and `qemu.go` instance fields. `Diagnose` uses `hmp("info registers", cpu)` to collect register dumps.

## Risks and Test Signals

The code assumes one outstanding synchronous command at a time and skips all events. A failed capability negotiation clears encoder/decoder but leaves the raw conn for GC/close only through caller state. Type assertions assume HMP returns a string. Tests should use a fake QMP server to cover banner decode, capability failure, event skipping, error responses, missing returns, and HMP error text.
