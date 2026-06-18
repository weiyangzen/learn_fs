<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf_sock_filter.c -->
## sources/test-tools/strace/src/bpf_sock_filter.c

Purpose: Specializes classic BPF program printing for socket filters by decoding socket ancillary load offsets.

Important APIs and types: Static `print_sock_filter_k` callback, exported `print_sock_fprog`, and exported `decode_sock_fprog`.

Control flow: For `BPF_LD | BPF_ABS` instructions, `print_sock_filter_k` recognizes `SKF_AD_OFF`, `SKF_NET_OFF`, and `SKF_LL_OFF` ranges. It prints the base symbolic constant plus offset or ancillary field name; otherwise generic BPF formatting prints the raw `k`.

State and persistence: No persistent state.

Dependencies and integration: Depends on `bpf_filter.h`, `<linux/filter.h>`, `xlat/skf_ad.h`, and `xlat/skf_off.h` constants. Used by socket-option decoders that inspect filter programs.

Risks: Only absolute load offsets receive socket-specific formatting. New kernel socket filter pseudo offsets need xlat updates to avoid `SKF_AD_???`.

Test signals: Socket filter tests should include ancillary, network, link-layer, and ordinary absolute offsets.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf_sock_filter.c -->
