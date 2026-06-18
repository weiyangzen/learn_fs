# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/StackedProgress.tsx

Purpose: Draws a horizontal proportional strip from capacity segment values.

Important APIs, types, and functions: Exports `StackedProgress` with `segments: Segment[]`.

Control flow: Memoizes total segment value, renders an empty placeholder if total is zero, otherwise maps each segment to a div with percentage width and background color.

State and persistence behavior: Pure derived render.

Dependencies: Uses React `useMemo` and the global `Segment` type available in the project typings/import context.

Integration points: Used by `CapacityBreakdown`.

Risks and edge cases: The file references `Segment` without importing it, relying on ambient/global type availability or causing a TypeScript error depending on config. Negative segment values can produce negative widths.

Test signals: Typecheck import behavior, zero total, single/multiple segments, negative values, and stable keys for duplicate labels.
