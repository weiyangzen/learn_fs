# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/ana.c

## Purpose
Mock-ioctl tests for atomic ANA log retrieval.

## Test Coverage
Covers invalid retry count, too-small header buffer, no groups, one/multiple ANA groups with and without namespace ID lists, RGO groups-only mode, multi-PDU reads, change-count retry/refetch behavior, max retry exhaustion, and buffer-too-short handling.

## Behavior
Each test constructs expected mock admin Get Log Page commands with precise `cdw10`, RAE/LSP bits, LPOL offsets, transfer lengths, and output data. It then calls `libnvme_get_ana_log_atomic()` and compares returned log bytes and adjusted length.

## Relevance
Validates robust ANA multipath state log retrieval, especially consistency under changing `chgcnt` and log sizes larger than one PDU.
