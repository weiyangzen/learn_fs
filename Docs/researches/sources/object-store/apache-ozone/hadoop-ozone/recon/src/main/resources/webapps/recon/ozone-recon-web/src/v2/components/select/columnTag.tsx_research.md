# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/columnTag.tsx

Purpose: Legacy/parked helper that renders closable selected-column tags into an external container using a React portal.

Important APIs, types, and functions: Exports `ColumnTag` and `TagProps` with `label`, `closable`, `tagRef`, and `onClose`.

Control flow: If `tagRef.current` exists, it creates an AntD `Tag` portal. Mouse down is prevented to avoid accidental text selection while closing a tag.

State and persistence behavior: No internal state and no persistence. Rendering depends entirely on the external DOM ref.

Dependencies: Uses Ant Design `Tag` and `createPortal` from `react-dom`.

Integration points: Kept for possible future column-filter display; current comments say the design no longer uses these tags.

Risks and edge cases: Defaulting `tagRef` to `null` conflicts with the declared `React.RefObject` type. Because it portals into arbitrary DOM, lifecycle timing and missing refs cause silent no-render behavior.

Test signals: If revived, test absent ref, close callback label propagation, mouse-down prevention, and cleanup when the portal target unmounts.
