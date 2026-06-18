# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/CapacityDetailError.tsx

Purpose: Small inline error row for unavailable capacity detail data.

Important APIs, types, and functions: Exports `CapacityDetailError` with optional `message` and `testId`.

Control flow: Renders a disconnect icon and message inside a `capacity-detail-error` div.

State and persistence behavior: Stateless.

Dependencies: Uses React and `DisconnectOutlined`.

Integration points: Displayed by `CapacityDetail` for SCM or other detail cards with unavailable metrics.

Risks and edge cases: Only a visual message; no retry/action. Test ID is optional and consumer-controlled.

Test signals: Snapshot default/custom messages and test-id propagation.
