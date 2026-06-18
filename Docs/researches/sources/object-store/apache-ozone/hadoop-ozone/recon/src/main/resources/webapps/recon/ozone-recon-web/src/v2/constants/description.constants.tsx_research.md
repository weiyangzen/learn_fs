# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/description.constants.tsx

Purpose: Defines reusable quota description labels with inline Ant Design popovers.

Important APIs, types, and functions: Exports JSX constants `QuotaInNamespace`, `QuotaUsed`, and `QuotaAllowed`.

Control flow: Each constant renders label text and an `InfoCircleOutlined` inside an AntD `Popover` with explanatory content.

State and persistence behavior: Static JSX constants only.

Dependencies: Uses React, AntD `Popover`, and `InfoCircleOutlined`.

Integration points: Consumed by quota-related table/card headers in Recon UI.

Risks and edge cases: JSX constants are created at module load and cannot be parameterized or localized. Text contains a minor grammar issue (`it's quota`).

Test signals: Snapshot/popover tests for labels, placement, icon class, and consumer rendering.
