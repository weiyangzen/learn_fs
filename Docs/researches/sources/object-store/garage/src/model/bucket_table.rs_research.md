# sources/object-store/garage/src/model/bucket_table.rs

## Purpose
This file defines Garage's replicated bucket metadata model. It stores bucket identity, deletion state, access-key permissions, global/local alias reverse indexes, website configuration, CORS rules, lifecycle rules, and quotas as CRDT state.

## Important APIs, types, and functions
`Bucket` contains an immutable UUID and `crdt::Deletable<BucketParams>`. `BucketParams` holds creation time, `authorized_keys`, alias reverse maps, website/CORS/lifecycle configs, and `BucketQuotas`. Public config types include `WebsiteConfig`, `RedirectAll`, `RoutingRule`, `RedirectCondition`, `Redirect`, `CorsRule`, `LifecycleRule`, `LifecycleFilter`, and `LifecycleExpiration`. `parse_lifecycle_date` accepts `YYYY-MM-DD` or midnight `YYYY-MM-DDTHH:MM:SSZ`. `Bucket::new`, `present`, `is_deleted`, `params`, `params_mut`, `authorized_keys`, `aliases`, and `local_aliases` are core accessors. `BucketTable` uses table name `bucket_v2`.

## Control flow
Bucket creation builds `BucketParams::new` with current millisecond creation time and empty CRDT maps. Mutations are generally performed through `LockedHelper`, which modifies both bucket reverse maps and the authoritative alias/key tables. `BucketParams::merge` keeps the earliest creation date, merges permissions and aliases, and LWW-merges configs/quotas.

## State and persistence behavior
The current format is `v2` with marker `G2bkt`; it migrates from `v08` by expanding website config with redirect/routing placeholders while preserving old permissions, aliases, CORS, lifecycle, and quota values. Deleted buckets retain their UUID and tombstone state. Reverse alias maps are advisory, used for listing and repair rather than as the authoritative source for global alias lookup.

## Dependencies and integration points
This table is fully replicated by `Garage::new`. It feeds S3 bucket authorization, admin bucket APIs, website/CORS/lifecycle handlers, lifecycle worker policy lookup, quota checks, object listing by bucket UUID, K2V bucket emptiness checks, and `LockedHelper::repair_aliases`.

## Risks and edge cases
Reverse alias state can diverge from `bucket_alias_table` or key-local aliases if paired writes partially fail or concurrent nodes mutate aliases; `repair_aliases` exists to correct this. Lifecycle date parsing rejects non-midnight datetimes, and invalid persisted lifecycle dates are only warned about by the lifecycle worker. Quota CRDTs use `AutoCrdt` with warning on differences, so concurrent conflicting quota edits require scrutiny.

## Test signals
No direct tests are present. Good signals should cover migration from v08, lifecycle date parsing, CRDT merge of permissions/configs, deletion tombstones, alias reverse-map repair, and lifecycle/quotas integration.
