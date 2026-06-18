# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/select.constants.tsx

Purpose: Centralizes `react-select` styling for Recon single and multi select controls.

Important APIs, types, and functions: Exports `selectStyles` as a `StylesConfig`.

Control flow: Style callbacks customize control border, option selected/active colors, menu shadow, placeholder color, hidden separator, and portal z-index.

State and persistence behavior: Static style object only.

Dependencies: Imports `StylesConfig` and the shared multi-select `Option` type.

Integration points: Used by `MultiSelect` and cast for `SingleSelect`.

Risks and edge cases: Typed for multi-select but reused for single-select. Uses hard-coded colors and z-index 9999, which can conflict with AntD modals/dropdowns.

Test signals: Visual regression for focused/selected/active states, portal stacking over tables/modals, and single-select compatibility.
