# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/log.c

This file centralizes syslog output for deliveries, remote forwards, and refusals. It unescapes sender/receiver strings, traces parent alias roots, includes dates and message size, and formats multi-line refusal text with `error+` prefixes.

`logdelivery()` logs one local delivery, `loglist()` drains and logs a list of remote/grouped destinations, and `logrefusal()` builds a bounded refusal log record. The functions mutate destination lists where they remove entries, so callers should treat passed lists as consumed.
