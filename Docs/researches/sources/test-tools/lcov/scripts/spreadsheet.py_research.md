# sources/test-tools/lcov/scripts/spreadsheet.py

Purpose: converts lcov/geninfo/genhtml profile JSON files into an Excel workbook for performance analysis, including per-tool worksheets, optional summary sheets, statistics, and conditional highlighting of outliers.

Important APIs/types: executable Python script using class `GenerateSpreadsheet(excelFile, files, args)`. CLI options include `-o`, `--threshold`, `--low`, `--high`, `-v/--verbose`, `--show-filter`, and profile JSON filenames. Internally, nested helpers insert conditional formats, statistics rows, data sections, and per-tool layouts.

Control flow and state: the constructor opens an `xlsxwriter.Workbook`, creates a summary sheet when multiple files are present, loads each JSON, identifies the tool from `data['config']['tool']` (with `lcov --call-from-lcov` treated as geninfo), creates a sanitized worksheet name, writes config and total rows, then dispatches profile-specific table generation for lcov segments, geninfo chunks/files/filter phases, genhtml scopes, or generic fallback keys. Summary formulas link back to individual worksheets.

Dependencies and integration: depends on `xlsxwriter`, JSON profile schemas emitted by lcov tools, and is wired into `tests/common.mak` as `SPREADSHEET_TOOL`; top-level test `Makefile` uses it in the `excel` target.

Risks and test signals: global threshold CLI options are parsed but not assigned back to module globals. Many broad `except` blocks skip corrupt data silently. Worksheet names may collide after truncation but have retry logic. Tests should run the `excel` target against generated JSON profiles and inspect workbook creation rather than full cell fidelity.
