# sources/object-store/rustfs/crates/madmin/src/site_replication.rs

Purpose: large wire-contract module for site replication administration: peer/site membership, IAM and bucket metadata replication, IDP settings, status summaries, replication metrics, remove/edit/resync operations, and site network performance results.

Important APIs/types/functions: `SITE_REPL_API_VERSION` is `"1"`. Core topology types include `PeerSite`, `PeerInfo`, `SiteReplicationInfo`, `SRPeerJoinReq`, `SRStateInfo`, `SRStateEditReq`, and `SyncStatus`. IAM/bucket change models include `SRPolicyMapping`, `SRSTSCredential`, `SRExternalUser`, `SRLDAPUser`, `SRIAMUser`, `SRGroupInfo`, `SRSvcAccUpdate/Delete/Change`, `SRCredInfo`, `SRIAMItem`, `SRBucketMeta`, `SRBucketInfo`, `SRIAMPolicy`, and `ILMExpiryRule`. Status/metrics types include `SRStatusInfo`, per-entity mismatch summaries, `SRSiteSummary`, `SRMetricsSummary`, `SRMetric`, queue/worker/window counters, and `SiteNetPerfResult`.

Control flow: only helper logic is `deserialize_vec_null_default`, which turns `null` site lists into empty vectors. Behavior is otherwise serde mapping, defaults, and omission of empty fields.

State and persistence: no direct persistence. The structs mirror replicated configuration and operational snapshots, heavily using `BTreeMap` for deterministic maps and timestamp fields for conflict/age visibility.

Dependencies/integration: imports group/user service-account types from the crate, serde, `serde_json::Value`, `HashMap`/`BTreeMap`, and `time::OffsetDateTime`. It is glob re-exported by `lib.rs`, so schema stability is externally visible.

Risks: the module carries many exact JSON field names, including mixed casing and hyphenated names; compatibility can break with small rename changes. Sensitive fields such as access keys and secret keys are present in serializable structs. Many values are generic `Value` or `String`, so semantic validation is elsewhere.

Test signals: no local tests in this file. Confidence comes from serde derives and downstream API tests; high-value additions would cover null-vector compatibility, timestamp serialization, and representative SR status round trips.
