# File Research: sources/os/bsd/openbsd-src/sbin/pflogd/pflogd.h

## Purpose

Shared constants and prototypes for `pflogd`.

## Contents

Defines capture and buffering defaults: `DEF_SNAPLEN`, `PCAP_TO_MS`, `PCAP_NUM_PKTS`, `PCAP_OPT_FIL`, `FLUSH_DELAY`, default log file, default interface, maximum snaplen, and output buffer size.

Declares logging, privilege-separation, pcap initialization/filtering, and fd-passing APIs used across `pflogd.c`, `privsep.c`, and `privsep_fdpass.c`. Also declares global `Debug`.

## Coupling

This header includes `pcap.h` and system limits because the public constants and prototypes use pcap-related types and integer bounds.
