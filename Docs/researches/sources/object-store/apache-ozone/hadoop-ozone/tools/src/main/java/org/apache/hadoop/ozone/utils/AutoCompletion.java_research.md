# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/utils/AutoCompletion.java

## Purpose
CLI command `ozone completion` for generating shell completion scripts for Ozone commands.

## Important APIs, types, and functions
Extends `GenericCli`, has `bash` and `zsh` subcommands, scans configured packages with Reflections for `GenericCli` subclasses, instantiates their picocli command models, filters public commands, and calls `AutoComplete.bash`.

## Control flow
`getBashCompletion` creates a synthetic top-level `ozone` command with common wrapper options, discovers command classes under HDDS/Ozone packages, adds public subcommands by stripping an `ozone ` prefix, and returns generated bash completion. Zsh currently emits the same bash script.

## State and persistence behavior
No persistent state. It performs runtime classpath scanning and writes generated script text to stdout.

## Dependencies and integration points
Integrates picocli autocomplete, HDDS GenericCli command metadata, Reflections classpath scanning, and Ratis `ReflectionUtils` instantiation.

## Risks and edge cases
Classpath scanning can be slow or incomplete depending on packaging. Commands without no-arg constructors are skipped. Zsh behavior may be bash-compatible rather than native zsh.

## Test signals
No direct tests here. Useful signals are generated script containing expected public commands and excluding hidden/default-name commands.
