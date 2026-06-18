# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_gbk2k.c

Read completely: 476 lines.

This module implements GBK/GB18030-style GBK2K ctype and stdenc support. It supports 1-byte ASCII, 2-byte GBK sequences, and optionally 4-byte surrogate-form sequences depending on module variables.

Key behavior: lead bytes are `0x81-0xFE`, trail bytes are `0x40-0x7E` or `0x80-0xFE`, and 4-byte sequences use decimal surrogate bytes `0x30-0x39` in positions 2 and 4. The variable parser scans for `2byte` to force `mb_cur_max = 2`; otherwise max is 4. Standard encoding classifies ASCII as csid 0, EUC-like G1 as csid 1, extended 2-byte as csid 2, and 4-byte GBKUCS as csid 3.

Important interactions: exports through ctype/stdenc templates and uses BCS case-insensitive matching for variables.

Security/reliability notes: conversion uses a small fixed 4-byte state buffer and checks each pushed byte class before completion. On `EILSEQ`, `mbrtowc_priv` does not reset `psenc->chlen`, unlike some peer modules; callers that retry after errors should explicitly reinitialize state.
