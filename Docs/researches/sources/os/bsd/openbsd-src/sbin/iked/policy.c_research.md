# File Research: sources/os/bsd/openbsd-src/sbin/iked/policy.c

This OpenIKED file owns policy lookup, IKE SA lifecycle state, SA indexing, traffic selector generation, address-pool/user lookup trees, active flow/CHILD SA comparison, and proposal negotiation.

Key responsibilities:
- Initializes policy, OCSP, RADIUS, user, SA, destination-ID SA, active-SA, and active-flow queues/trees in `policy_init`.
- Matches inbound IKE messages or existing SAs to configured policies through `policy_lookup`, `policy_lookup_sa`, `policy_test`, and `policy_test_flows`.
- Uses pf-style skip-step acceleration in `policy_calc_skip_steps` to jump across policies that cannot match by flags, address family, peer address, or local address.
- Reference-counts reload-surviving policies with `policy_ref` and `policy_unref`.
- Maintains SA state transitions, required validation flags, and iked statistics in `sa_state`, `sa_stateflags`, and `sa_stateok`.
- Allocates or reuses IKE SAs in `sa_new`, inserts them into RB trees keyed by initiator/SPI, attaches policy references, and initializes required authentication/certificate/EAP state flags.
- Builds traffic selector lists from configured flows with duplicate suppression in `policy_generate_ts` and `ts_insert_unique`.
- Frees IKE SAs, rekey links, destination-ID tree entries, flows, CHILD SAs, and associated policy references via `sa_free`, `sa_free_flows`, `childsa_free`, and `flow_free`.
- Configures virtual interface state for Configuration Payload-assigned DNS/address/routes in `sa_configure_iface`, delegating OS changes to `vroute.c`.
- Provides SA lookup by SPI and by authenticated destination ID through `sa_lookup`, `sa_dstid_lookup`, `sa_dstid_insert`, and `sa_dstid_remove`.
- Negotiates local/peer proposals with transform scoring through `proposals_negotiate` and `proposals_match`.

Important data structures:
- TAILQs for policies, flows, policy SA peers, and traffic selectors.
- RB trees generated at the bottom of the file for IKE SAs, destination-ID-indexed SAs, address pools, users, active CHILD SAs, and flows.
- `struct iked_policy`, `struct iked_sa`, `struct iked_flow`, `struct iked_childsa`, and `struct iked_proposal` are central callers/consumers.

Security and correctness notes:
- Policy matching requires compatible address family, peer/local prefixes, IDs, transport-mode setting, flows, and proposal transforms.
- Proposal matching handles AEAD transforms by rejecting separate integrity transforms and requiring mandatory transform classes for IKE, AH, and ESP.
- Destination-ID indexing is deliberately strict: missing/corrupt IDs are fatal because the RB-tree comparator depends on valid ID buffers.
- `sa_configure_iface` directly ties negotiated CP state to interface address/DNS/route side effects; failures propagate as SA configuration failures.
