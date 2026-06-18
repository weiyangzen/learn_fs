<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/table-ui.go -->
# sources/object-store/minio-mc/cmd/table-ui.go

Purpose: provides a tiny shared color abstraction for table/status UIs.

Important APIs/types/functions: `col` string type, color constants (`colGrey`, `colRed`, `colYellow`, `colGreen`), and `getPrintCol`.

Control flow: `getPrintCol` maps symbolic color names to bold terminal colors from `fatih/color`; unknown values return nil.

State and persistence: no persistent state. It allocates color objects per call.

Dependencies and integration points: used by terminal/table rendering code elsewhere in the command package when status colors are represented as values instead of direct `color.Color` instances.

Risks and test signals: low risk, but nil on unknown color requires callers to handle absence. Tests should assert mappings and unknown behavior if callers depend on non-nil colors.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/table-ui.go -->
