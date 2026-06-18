# File Research: sources/os/bsd/netbsd-src/sys/sys/idle.h

Read completely: 37 lines.

## Purpose
Declares CPU idle loop and idle LWP creation functions.

## Main Interfaces
- Forward declaration `struct cpu_info`.
- `idle_loop(void *)`.
- `create_idle_lwp(struct cpu_info *)`.

## Dependencies And Integration
Scheduler/CPU initialization infrastructure consumes this header.

## Risks And Edge Cases
- Architecture and scheduler code must create one idle LWP per CPU as expected by the implementation.

## Filesystem Relevance
Low. General scheduler infrastructure.
