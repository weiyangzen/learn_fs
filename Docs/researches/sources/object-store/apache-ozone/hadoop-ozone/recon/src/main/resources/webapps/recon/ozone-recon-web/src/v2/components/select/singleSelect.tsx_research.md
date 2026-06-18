# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/singleSelect.tsx

Purpose: Wraps `react-select` as a compact single-value selector with Recon styling and a custom value label prefix.

Important APIs, types, and functions: Exports `SingleSelect` and `Option`. Props extend non-multi `react-select` props and add `options`, `placeholder`, and `onChange`.

Control flow: Renders a non-clearable, non-searchable select. Custom `ValueContainer` displays `placeholder: selectedLabel` while preserving react-select's hidden dummy input child.

State and persistence behavior: Stateless controlled/defaulted select; selected value is managed by parent via react-select props.

Dependencies: Uses `react-select` and shared `selectStyles`.

Integration points: Used for limit selectors and similar single-choice controls across buckets and insights tables.

Risks and edge cases: Style type is cast from a multi-select `StylesConfig`, and the child-name check depends on react-select internals. Like other selectors it portals to `document.body`.

Test signals: Cover default value display, onChange value shape, empty selection rendering, disabled inherited props, and menu portal z-index with AntD tables.
