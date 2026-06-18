# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/search/search.tsx

Purpose: Provides a compact Ant Design search input with an optional column selector prefix for Recon table filters.

Important APIs, types, and functions: Exports `Search`. Props include disabled state, current search column, input value, optional `Option[]` search choices, `onSearchChange`, and selector `onChange`.

Control flow: If `searchColumn` is provided, the component renders an AntD `Select` in `addonBefore`; otherwise it renders a plain `Input`. Search text is controlled by the parent and `allowClear` is enabled.

State and persistence behavior: Stateless controlled component; all search text and selected column persistence live in parent pages.

Dependencies: Uses Ant Design `Input` and `Select`, `DownOutlined`, and the shared single-select `Option` shape.

Integration points: Shared by Buckets, Containers, Datanodes, Pipelines/Volumes-style pages, and several insights tables.

Risks and edge cases: The select uses `defaultValue`, not `value`, so parent changes to `searchColumn` after mount may not be reflected. The dropdown arrow is hidden for single-option selectors, and handlers default to no-op, which can hide wiring mistakes.

Test signals: Verify controlled input clearing, disabled propagation, one-option versus multi-option suffix icon behavior, and changing search column resets parent search where expected.
