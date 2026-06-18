# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_text.h

This header defines IDM support for iSCSI text key-value negotiation and conversion between text buffers and `nvlist_t`.

Key definitions:
- `iscsikey_id_t` enumerates iSCSI login/text keys:
  - Authentication keys for KRB, SPKM, SRP, CHAP.
  - Operational keys such as HeaderDigest, DataDigest, MaxConnections, SendTargets, TargetName, InitiatorName, aliases, TargetAddress, TPGT, InitialR2T, ImmediateData, segment lengths, burst lengths, timers, outstanding R2T, ordering flags, ErrorRecoveryLevel, markers.
  - iSER keys such as RDMAExtensions and receive segment lengths.
- Comment notes the enum should stay under 64 values because login code uses a bitmask for negotiated key tracking.
- `idmkey_type_t` classifies values as text, iSCSI name, booleans, numerical, ranges, binary, simple, or list-of-values.
- `idm_kv_xlate_t` maps key IDs to names, value types, and declarative status.

Functions:
- Key lookup and ID/name conversion.
- Add key-value pairs to nvlists.
- Convert text buffers to nvlists and nvlists to text buffers.
- Determine first-fragment length.
- Convert nvlist status to `kv_status_t`, and key negotiation status to iSCSI error class/detail.
- Iterate list values and convert nvpair values to text.
- Convert PDU lists to nvlists.
- Create/free internal text buffers and initialize PDU text data.

Dependencies:
- Includes `sys/idm/idm_impl.h`.

Relevance:
- Critical for iSCSI login negotiation, SendTargets, and operational parameter exchange.
