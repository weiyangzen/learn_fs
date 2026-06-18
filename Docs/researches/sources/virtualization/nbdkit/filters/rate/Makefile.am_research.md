# File Research: sources/virtualization/nbdkit/filters/rate/Makefile.am

This fragment builds `nbdkit-rate-filter.la` from `bucket.c`, `bucket.h`, and `rate.c`. It includes core headers, replacements, and utilities, and links utility/replacement libraries plus the platform import library.

The POD manual is distributed and optionally generated. The build split reflects a reusable token-bucket implementation separated from the nbdkit filter wrapper.
