# sources/test-tools/syzkaller/vm/adb/adb_ppc64le.go

## Purpose

`adb_ppc64le.go` disables the ADB backend implementation on ppc64le while keeping package builds successful.

## Important APIs, Types, and Functions

The file contains only the `package adb` declaration under normal Go source syntax. There are no exported functions or types.

## Control Flow

There is no runtime control flow. Build selection excludes `adb.go` on ppc64le and includes this placeholder instead.

## State and Persistence Behavior

No state is created or persisted.

## Dependencies and Integration Points

The comment explains that ppc64le lacks a `golang.org/x/sys/unix.TCGETS2` constant required by console code, so the backend is turned off on that platform.

## Risks and Test Signals

The risk is silent absence of ADB VM registration on ppc64le. Build tests for ppc64le should verify the package compiles and syzkaller reports unsupported backend behavior cleanly.
