# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/limit.constants.tsx

Purpose: Defines shared row-limit options for select controls.

Important APIs, types, and functions: Exports `LIMIT_OPTIONS` as `Option[]` with 1000, 5000, 10000, and 20000 values.

Control flow: Static list only.

State and persistence behavior: No state.

Dependencies: Imports `Option` from `singleSelect`.

Integration points: Used by Buckets and Insights tables to build API `limit` query parameters.

Risks and edge cases: Option values are strings and must be parsed or accepted by APIs. Large defaults can be expensive for browser rendering and backend queries.

Test signals: Confirm consumers pass expected string values to APIs and handle each limit without pagination regressions.
