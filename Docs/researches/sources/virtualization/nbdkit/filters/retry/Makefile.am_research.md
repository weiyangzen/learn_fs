# File Research: sources/virtualization/nbdkit/filters/retry/Makefile.am

This fragment builds `nbdkit-retry-filter.la` from `retry.c`, includes core headers and `common/utils`, and links utility/replacement libraries plus platform import support. It distributes and optionally builds the manual.

Unlike `retry-request`, this filter needs backend context reopen support, but the build-time dependencies remain within the nbdkit filter API and common utilities.
