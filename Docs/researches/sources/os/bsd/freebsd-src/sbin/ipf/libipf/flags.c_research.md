# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/flags.c

This file defines shared TCP flag display data.

It provides fallback definitions for ECN/CWR/AE flag bits and exports `flagset[] = "FSRPAUEWe"` plus a parallel `flags[]` array of TCP flag masks. Printing/parsing helpers use these arrays to map between bit flags and compact letters.
