# sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkCfg.hh

## Purpose
`XrdNetPMarkCfg.hh` declares the concrete configuration-backed implementation of `XrdNetPMark`. It is the public bridge between server configuration parsing and runtime packet-marking handles.

## Important APIs, Types, and Functions
The class overrides both `Begin()` overloads from `XrdNetPMark`, exposes static `Config()` for final service construction, and static `Parse()` for `pmark` directive parsing. Private static helpers mirror the implementation phases: definition loading, mapping setup, JSON processing, display, and code lookup.

## Control Flow and State
The header makes the lifecycle explicit: `Parse()` is called while reading configuration, `Config()` resolves and validates accumulated static state, and runtime callers use `Begin()` to obtain per-flow handles. The constructor is public and trivial, while the destructor is private, reinforcing that service instances are not meant to be deleted through ordinary callers.

## Dependencies and Integration Points
It includes `XrdNetPMark.hh` and forward-declares logging, scheduler, stream, map, and trace classes. It is included by xrootd configuration code and by its own implementation.

## Risks and Test Signals
The private destructor and static mutable configuration make ownership and reconfiguration behavior important. Tests should verify that parsing can happen before construction, that disabled configurations return null without leaks or fatal state, and that `Begin()` behavior matches the configured maps and flags.
