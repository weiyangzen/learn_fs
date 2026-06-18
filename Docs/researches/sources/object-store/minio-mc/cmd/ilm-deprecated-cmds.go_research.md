# Research: sources/object-store/minio-mc/cmd/ilm-deprecated-cmds.go

Purpose: preserves hidden legacy `mc ilm add/rm/edit/ls/export/import` entry points while the visible command surface uses `mc ilm rule ...`.

Important APIs/types/functions: `ilmDepCmds` and hidden command variables `ilmDepAddCmd`, `ilmDepRmCmd`, `ilmDepEditCmd`, `ilmDepLsCmd`, `ilmDepExportCmd`, `ilmDepImportCmd`.

Control flow: each deprecated command points to the same handler and flags as the newer rule subcommand. `Hidden: true` keeps them out of normal help output while retaining compatibility.

State and persistence: no direct state changes here; handlers mutate or read bucket lifecycle configuration.

Dependencies/integration points: depends on ILM rule handlers and flags declared in rule files.

Risks: compatibility wrappers can drift from current help text or flag behavior if new rule flags are not reused. Hidden commands still affect CLI behavior and should be tested before removal.

Test signals: no direct tests; backward-compatibility CLI tests should assert hidden aliases still work.
