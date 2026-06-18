# File Research: sources/os/bsd/freebsd-src/sbin/routed/input.c

RIP packet receive path, request/response processing, authentication validation, and route-update ingestion.

Key responsibilities:
- Reads RIP datagrams from global or per-interface UDP sockets.
- Determines the authenticated/expected incoming interface using source address or `SO_PASSIFNAME` interface metadata.
- Validates RIP versions, lengths, commands, source ports, enabled input policy, and router trust.
- Answers full-table and specific-route RIP requests, including query-specific security controls.
- Handles trace on/off RIP commands from privileged ports and known routers.
- Processes RIP responses with metric, mask, next-hop, default-route, and trusted-gateway filtering.
- Deaggregates received RIPv2 routes when RIPv1 output requires more specific routes.
- Updates primary/spare route slots through `input_route()`.
- Validates cleartext and MD5 RIPv2 authentication with key lifetimes and key IDs.

Dependencies:
- Uses route table APIs (`rtget`, `rtfind`, `rtadd`, `rtchange`, `rtswitch`), interface lookup/state, output buffers from `output.c`, auth structures, MD5, and rate-limited logging.

Notable risks:
- Authentication deliberately accepts unauthenticated RIPv2 when no secrets are configured, matching historic behavior but not strong security.
- The code contains many compatibility choices for RIPv1/RIPv2 interoperability that affect route masks and aggregation.
- Incorrect source-interface classification can cause legitimate routes to be rejected or malicious routes to be accepted.
