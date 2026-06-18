# Research: sources/object-store/minio-mc/cmd/ilm-main.go

Purpose: registers the top-level `mc ilm` namespace and shared display color names.

Important APIs/types/functions: `ilmSubcommands`, `ilmCmd`, `mainILM`, constants for color themes, and `setILMDisplayColorScheme`.

Control flow: dispatches visible subcommands `rule`, `tier`, and `restore`, plus hidden deprecated commands. `setILMDisplayColorScheme` configures console colors used by rule output.

State and persistence: no server or local persistence. It only configures CLI routing and console color state.

Dependencies/integration points: depends on rule, tier, restore, and deprecated command variables.

Risks: color theme names are referenced across ILM files; renaming breaks formatting. Hidden deprecated commands are appended to the main command and remain runnable.

Test signals: command-tree smoke tests and simple color setup coverage if console output tests exist.
