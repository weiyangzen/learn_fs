# sources/test-tools/syzkaller/pkg/subsystem/linux/names_test.go

## Purpose

This file tests Linux subsystem name derivation from mailing lists and validates collision/error behavior in `setSubsystemNames`.

## Important APIs, Types, and Functions

`TestEmailToName` exercises `emailToName`. `subsystemTestInput` is a small fixture helper that converts input name/email pairs into `*subsystem.Subsystem`. `TestSetSubsystemNames` runs table-driven cases through `setSubsystemNames`.

## Control Flow

Email tests verify general prefix/suffix stripping, dot removal, and an exception for virtualization. Naming tests cover successful generation, duplicate generated names, missing list failure, preserving explicit names, and collisions between an explicit name and a generated name. The test then checks either expected failure or final names by list index.

## State, Dependencies, Risks, and Test Signals

All state is fixture-local and mutations occur on newly allocated subsystem objects. Dependencies are `testing` and the local `subsystem` type. The tests provide good signal for common name derivation and collision protection. They do not cover all exception-map entries, invalid email formats that fail the regex, minimum/maximum length boundaries directly, multiple lists per subsystem, or nondeterminism from future changes to list ordering upstream.
