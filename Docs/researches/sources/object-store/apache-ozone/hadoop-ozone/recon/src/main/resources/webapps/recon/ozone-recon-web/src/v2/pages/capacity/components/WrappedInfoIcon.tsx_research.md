# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/WrappedInfoIcon.tsx

Purpose: Reusable tooltip-wrapped info icon for capacity labels.

Important APIs, types, and functions: Exports `WrappedInfoIcon` with `title` and optional AntD tooltip placement.

Control flow: Renders an `InfoCircleOutlined` styled in blue with a tooltip.

State and persistence behavior: Stateless.

Dependencies: Uses AntD `Tooltip` and info icon.

Integration points: Used throughout Capacity labels and descriptions.

Risks and edge cases: Title is typed as string only, so rich tooltip content requires different components. Inline style duplicates icon styling.

Test signals: Check placement default/override, title rendering, and icon style/class integration.
