# File Research: sources/os/plan9/9front/sys/src/cmd/pcc.c

## Role

Acts as an APE C compiler driver, wrapping Plan 9 architecture-specific compiler, linker, and preprocessor commands.

## Main Behavior

`findoty` reads `$objtype` and selects tool names/extensions from `objtype[]`. The driver builds command lists for `cpp`, the architecture compiler, and linker.

C sources are preprocessed through `/bin/cpp` and piped to the compiler. Object/library inputs are accumulated for the linker. Unless compile-only mode is selected, the linker is invoked with the selected output name and APE support library.

## Options

Handles common compile/link/preprocess flags including `-c`, `-o`, `-l`, `-D`, `-I`, `-U`, verbose mode, preprocessor-only modes, profiling, assembler-output variants, and several compiler pass-through flags. Wrong-architecture object arguments are ignored with a warning.

## Process Handling

`doexec` runs a single command and checks wait status. `dopipe` connects preprocessor output to compiler input and waits for both children. Verbose mode prints the composed command lines.
