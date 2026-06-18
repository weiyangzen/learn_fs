# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_wr.h

## Role

`hermon_wr.h` defines Hermon work-request and WRID tracking helpers. It provides macros for WQE address calculations, CQE WQE-token extraction, send-WQE ownership updates, special-QP directed-route MAD handling, and work-queue bookkeeping structures.

## Major Definitions

The WQE macros compute queue entries for QP send queues, QP receive queues, and SRQs from queue base plus tail index and WQE-size shift. SRQ helpers convert between WQE addresses and SRQ WQE indexes.

`HERMON_SET_SEND_WQE_OWNER()` writes the send WQE owner/opcode field. `HERMON_CQE_WQEADDRSZ_GET()` extracts the CQE WQE address/size token.

Directed-route MAD macros locate management class, hop pointer, and hop count fields across possibly fragmented buffers, then adjust the hop pointer for outbound/inbound directed-route MAD processing.

`hermon_workq_hdr_s` tracks WRID circular queue state: queue size, mask, WRID array, head, tail, and full flag. `hermon_workq_avl_s` links work queues into an AVL tree by QP number/type and carries SRQ metadata when completions must return SRQ WQEs to a free list. `HERMON_WR_RECV`, `HERMON_WR_SEND`, and `HERMON_WR_SRQ` classify work-queue types.

## Interfaces

The file declares post-send, post-receive, and post-SRQ routines; WRID reset handling; CQE-to-WRID lookup; work-queue header create/destroy helpers; an AVL comparator; and a debug QP check routine.

## Integration Notes

This header sits on the Hermon fast path. The work-queue and WRID structures bridge posted IBTF work requests to later CQ completions, including SRQ-specific completion recycling.
