# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/ReconAIMark.tsx

Purpose: Inline SVG mark for Recon AI avatars, hero, and active loading states.

Important APIs, types, and functions: Exports `ReconAIMark` with optional `size`, `active`, and `className`.

Control flow: Defines a reusable sparkle path and places four scaled `use` instances in a group, applying CSS classes for active animation/styling.

State and persistence behavior: Stateless.

Dependencies: No external UI dependencies beyond React/SVG.

Integration points: Used by Assistant header, empty state, message bubbles, loading indicator, and error bubble.

Risks and edge cases: SVG IDs can collide if embedded in complex documents, though scoped use is usually fine. Styling/animation depends on external CSS classes.

Test signals: Snapshot size/class/active output and verify avatar contexts inherit color correctly.
