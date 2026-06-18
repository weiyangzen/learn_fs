# File Research: sources/os/bsd/openbsd-src/sbin/iked/ikev2.c

## Role

`ikev2.c` is the main IKEv2 protocol engine for OpenBSD `iked`. It handles the IKEv2 process lifecycle, privileged-process message dispatch, IKE packet receive/demux, initiator and responder exchanges, authentication, child-SA negotiation, rekeying, NAT-T/MOBIKE/configuration payload handling, PF_KEY installation hooks, timers, and diagnostic reporting.

Although this file is under the OpenBSD source tree in subset A, its domain is IPsec/IKE daemon control-plane logic rather than filesystem logic.

## Process and Control Plane

The file registers the IKEv2 process with three peer privsep channels: `parent`, `certstore`, and `control`. `ikev2_run()` pledges `stdio inet recvfd`, and `ikev2_shutdown()` frees the cached local CERTREQ and resets configuration.

`ikev2_dispatch_parent()` accepts runtime configuration and socket setup messages, including reset/couple/mode changes, UDP and PF_KEY sockets, policies, flows, users, RADIUS configuration, compile completion, and static configuration. On active/passive changes it regenerates traffic selectors, reconciles existing SAs against the new policy set, tears down orphaned or incomplete SAs, and schedules initiator startup when appropriate.

`ikev2_dispatch_cert()` is the asynchronous bridge to the certificate process. It updates local CERTREQ state, records peer certificate validation results, stores primary and supplemental certificates, receives locally generated AUTH payloads, and resumes IKE_AUTH once certificate or AUTH material is available. `ikev2_dispatch_control()` handles `ikectl`-style reset-by-ID, SA listing, and stats requests.

## Receive Path and State Dispatch

`ikev2_recv()` is the central inbound packet gate. It validates the IKE header and length, updates statistics, derives initiator/responder direction from flags, looks up the SA and policy, logs the exchange, checks message IDs and retransmit caches, handles request/response sequencing, and routes to either `ikev2_init_recv()` or `ikev2_resp_recv()`.

The receive path protects protocol ordering by dropping mismatched response IDs, unsolicited responses, unencrypted non-initial exchanges, duplicate in-flight requests, and invalid retransmits. It also records valid request message IDs and response history so retransmission handling can replay prior responses.

`ikev2_init_recv()` handles responses to locally initiated exchanges: `IKE_SA_INIT`, `IKE_AUTH`, `CREATE_CHILD_SA`, and `INFORMATIONAL`. It parses payloads, updates peer/local addresses, handles cookies, notifies, NAT detection, authentication failure, proposal failure, child-SA response handling, and informational completion.

`ikev2_resp_recv()` handles peer-initiated exchanges. It creates responder SAs for `IKE_SA_INIT`, validates existing SAs for later exchanges, parses payloads, updates addresses/socket metadata, processes notifications, enables NAT-T when needed, then calls responder handlers for SA_INIT, IKE_AUTH/EAP, CREATE_CHILD_SA, and INFORMATIONAL.

## IKE SA Initialization and Authentication

`ikev2_init_ike_sa()` scans active policies and starts initiator exchanges. `ikev2_init_ike_sa_peer()` constructs an `IKE_SA_INIT` request with SA, KE, nonce, optional cookie reflection, vendor ID, fragmentation support, NAT detection, and signature-hash notification. It stores the first message for later AUTH calculations and arms an exchange timeout.

`ikev2_resp_ike_sa_init()` builds the responder’s `IKE_SA_INIT` response with negotiated SA, KE, nonce, optional vendor/fragmentation/NAT/CERTREQ/signature-hash payloads, and stores the second message for AUTH.

Authentication is split between local synchronous checks and the certificate process. `ikev2_ike_auth_recv()` records peer IDs, redoes policy lookup based on authenticated IDs, bundles received certificate chains, negotiates CHILD_SA proposals from IKE_AUTH, captures CP replies, validates PSK/EAP directly, or asks the certificate process to validate certificate/public-key authentication. `ikev2_auth_verify()` verifies AUTH payloads, including EAP-derived MSK as PSK material, and advances EAP/auth state.

`ikev2_init_ike_auth()` creates initiator IKE_AUTH encrypted content: IDi, optional IDr, CERT/CERTREQ, AUTH, CP request, IPCOMP/transport notifications, SA, and traffic selectors. `ikev2_resp_ike_auth()` creates responder IKE_AUTH content, including EAP identity challenge when needed, local ID/CERT/AUTH, CP reply, IPCOMP/transport/MOBIKE notifications, SA/TS payloads, then enables the CHILD SAs and marks the IKE SA established.

## Payload and Notification Builders

The file provides low-level packet construction helpers: `ikev2_add_header()`, `ikev2_set_header()`, `ikev2_add_payload()`, `ikev2_next_payload()`, `ikev2_add_data()`, and `ikev2_add_buf()`.

Higher-level builders encode traffic selectors, CERTREQs, IPCOMP notifications, generic notifies, vendor IDs, MOBIKE, fragmentation, signature-hash algorithms, transport mode, NAT detection, CP payloads, proposals, and transforms. `ikev2_nat_detection()` implements the RFC NAT-D SHA1 calculation over SPIs, IP address, and port, with deliberate digest distortion when NAT-T is forced.

`ikev2_handle_notifies()` interprets parsed notifies and mutates SA state: fragmentation, MOBIKE, NO_ADDITIONAL_SAS, INVALID_KE retry behavior, IPCOMP, NAT keepalives, signature-hash support, transport mode, and temporary-failure handling.

## Child SAs, Rekeying, and Deletion

`ikev2_send_create_child_sa()` initiates new CHILD_SA creation or CHILD/IKE SA rekey via CREATE_CHILD_SA, including nonce generation, proposal refresh, optional PFS KE, traffic selectors, and REKEY_SA notification.

`ikev2_resp_create_child_sa()` handles peer CREATE_CHILD_SA requests for IKE SA rekeying, CHILD_SA creation, and CHILD_SA rekeying. It negotiates proposals, validates PFS, tracks rekey targets, handles simultaneous CHILD rekeying via nonce comparison, and either records responder IKE rekey candidates or enables new child SAs.

`ikev2_ike_sa_rekey()` initiates IKE SA rekeying by creating a new SA, building CREATE_CHILD_SA with IKE proposals, nonce, and KE, and linking it as `sa_nexti`. `ikev2_ikesa_enable()` promotes a replacement IKE SA by transferring sockets, NAT/MOBIKE/fragmentation flags, addresses, flows, child SAs, proposals, identities, certificates, address-pool leases, CP state, tags, and accounting metadata from the old SA before deleting the old SA.

`ikev2_handle_delete()`, `ikev2_ikesa_delete()`, `ikev2_ikesa_recv_delete()`, `ikev2_childsa_delete()`, `ikev2_child_sa_drop()`, and `ikev2_childsa_delete_proposed()` implement delete payload processing and cleanup for IKE SAs, CHILD SAs, and bundled IPCOMP SAs.

## Key Derivation and Crypto Material

`ikev2_sa_initiator()`, `ikev2_sa_responder()`, and their DH helpers establish nonce, DH, proposal, cipher, integrity, and PRF state. `ikev2_sa_keys()` follows RFC7296 key derivation: computes DH shared secret, derives SKEYSEED, constructs `Ni | Nr | SPIi | SPIr`, runs `prf+`, and extracts SK_d, integrity keys when non-AEAD, encryption keys, and AUTH PRF keys. `ikev2_prfplus()` implements iterative IKEv2 `prf+`.

`ikev2_childsa_negotiate()` derives child-SA key material from SK_d plus nonces and optional PFS DH secret, creates inbound/outbound flows, creates paired child SAs, supports ESP/AH, ESN, AEAD/no-integrity cases, transport mode, and optional bundled IPCOMP SAs.

## Address Assignment, NAT-T, MOBIKE, and Timers

`ikev2_enable_natt()` switches an SA to the NAT-T socket and ports. `ikev2_update_sa_addresses()` updates PF_KEY SAs, reloads flows, updates retransmit packet addresses, and records the loaded peer address for MOBIKE/update-address handling.

Configuration payload handling includes `ikev2_cp_setaddr()`, `ikev2_cp_setaddr_pool()`, `ikev2_cp_fixaddr()`, `ikev2_cp_fixflow()`, and `ikev2_cp_request_configured()`. These allocate IPv4/IPv6 internal addresses from pools, honor RADIUS/requested addresses where supported, support sticky address reuse by destination ID, and patch unspecified flow/TS addresses with assigned leases.

Timers cover SA_INIT exchange timeout, delete timeout, liveness/DPD probes, NAT keepalives, and randomized or fast rekey scheduling. `ikev2_ike_sa_alive()` probes when outbound traffic or IKE idle state suggests the peer may be dead.

## Diagnostics

The bottom of the file implements `ikev2_info*()` control output for SAs, child SAs, flows, active SAs, active flows, and destination-ID SA indexes. Logging helpers format established SA summaries, certificate info, proposal details, and SPI-tagged messages.

## Important Dependencies

This file depends heavily on local `iked` subsystems: `sa_*`, `policy_*`, `config_*`, `ikev2_msg_*`, `ikev2_pld_parse()`, `pfkey_*`, `ca_*`, `eap_*`, RADIUS helpers, DH groups, cipher/hash abstractions, `ibuf`, timers, RB/TAILQ/SIMPLEQ collections, and OpenSSL SHA/EVP/X509 APIs.

## Research Notes

The implementation is stateful and protocol-dense. Correctness depends on preserving IKE message ordering, SA state flags, retransmission caches, ownership transfer of `ibuf` fields from parsed messages into SAs, and cleanup on every failure path. Rekeying is particularly delicate because old and new IKE SAs share and transfer child SAs, flows, leases, identities, timers, and accounting state.
