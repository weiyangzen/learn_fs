# sources/user-network-fs/nfs-ganesha/src/config_parsing/verif_syntax.c

## Purpose

`verif_syntax.c` is a command-line syntax checker for Ganesha configuration files.

## Important APIs, Types, and Functions

The only function is `main`. It uses `SetDefaultLogging`, `SetNamePgm`, `LogTest`, `config_ParseFile`, and `config_Free`.

## Control Flow

The program initializes test logging, requires one config file argument, calls `config_ParseFile`, logs an error and exits `EINVAL` if parsing fails, otherwise logs success and exits 0.

## State and Persistence Behavior

It creates a parse tree but exits immediately after logging success, making the subsequent `config_Free(config)` unreachable. It has no persistent state.

## Dependencies and Integration Points

It depends on the parser API and Ganesha logging. It is intended for build/test or operator syntax validation.

## Risks and Edge Cases

The call `config_ParseFile(fichier)` does not match the two-argument signature visible in `config_parsing.c`, suggesting API drift, macro overloading, or stale test code. The success path leaks the parse tree because it exits before freeing. The declared `errtxt` is unused.

## Test Signals

Build success is itself an API compatibility signal. Runtime tests should check valid/invalid configs and ensure the program returns shell-friendly status codes; leak checks would catch the unreachable free.
