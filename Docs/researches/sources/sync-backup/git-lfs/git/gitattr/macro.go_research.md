# sources/sync-backup/git-lfs/git/gitattr/macro.go

Purpose: expands Git attribute macros into concrete attributes while preserving the original macro attribute as Git does.

Important APIs/types/functions: `MacroProcessor`, `NewMacroProcessor`, `ProcessLines`, and `ProcessMacros`. The built-in `binary` macro expands to `-diff`, `-merge`, and `-text`.

Control flow: `ProcessLines` iterates parsed lines. Pattern lines are copied into new pattern lines with expanded attributes; macro attributes with value `true` append the macro expansion before the alias attribute, and unspecified macro attributes append unspecified versions of each macro member. Macro lines update the processor only when `readMacros` is true. `ProcessMacros` loads macro definitions without returning pattern lines.

State/persistence behavior: `MacroProcessor.macros` persists across calls and `didReadMacros` records whether macro definitions have been loaded for a tree. Macro definitions can be overridden by later processing.

Dependencies/integration: consumed by attribute file readers and `Tree.Applied` to match Git's stateful macro semantics.

Risks/test signals: statefulness is useful but requires careful call ordering. Tests cover enabled/disabled macros, unspecified macros, built-in binary, cross-call state, and macro overrides.
