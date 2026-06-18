# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_radix.c

## Purpose
Implements PF table/radix compatibility wrappers, interface query wrappers, and generic pfr buffer management.

## Main Elements
- Generates RB tree support for `pfr_ktablehead`.
- Wraps libpfctl and ioctl table operations: add/delete/get tables, add/delete/set/get/test addresses, clear stats, inactive define.
- Reports oversized PF request errors using `net.pf.request_maxcount`.
- Exposes `pfi_get_ifaces()` for interface stats retrieval.
- Defines `pfr_buffer` element sizes and buffer add/next/grow/clear routines.
- Loads address tokens from files/stdin with comment and whitespace handling.

## Dependencies And Integration
Uses global `dev` and `pfh`, PF table ioctls, libpfctl table functions, and `append_addr()` from parser helpers.

## Risk Notes
The shared buffer code underpins table parsing and loading. Incorrect element type, growth, or token parsing would corrupt table operations or misread table files.
