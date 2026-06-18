# File Research: sources/virtualization/nbdkit/filters/retry-request/Makefile.am

This build file compiles `nbdkit-retry-request-filter.la` from `retry-request.c`, includes core headers and `common/utils`, and links utility/replacement libraries plus platform import support. It distributes and optionally builds the filter manual.

The module implements per-request retry without reopening the backend, so its build dependencies are lighter than the full reconnecting retry filter.
