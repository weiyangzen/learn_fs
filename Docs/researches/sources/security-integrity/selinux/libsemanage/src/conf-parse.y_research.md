# sources/security-integrity/selinux/libsemanage/src/conf-parse.y

Purpose: bison grammar and implementation for parsing `semanage.conf`, creating a populated `semanage_conf_t` with defaults and user overrides.

Important APIs/types/functions: grammar tokens cover store settings, policy version, target platform, booleans such as `expand-check` and `optimize-policy`, bzip options, external command blocks, and verifier blocks. C helpers include `semanage_conf_parse`, `semanage_conf_destroy`, `semanage_error`, `parse_module_store`, `parse_store_root_path`, `parse_compiler_path`, and `new_external_prog`.

Control flow: `semanage_conf_parse` allocates defaults, opens the config file if present, invokes the lexer/parser, destroys lexer state, and returns defaults when the file cannot be read. Grammar actions validate values and update the current global config, aborting on fatal parse errors.

State and persistence behavior: parser state uses file-global `current_conf`, `new_external`, and `parse_errors`, so it is explicitly not thread-safe. It allocates strings and linked lists for external commands; destroy frees all owned members.

Dependencies and integration points: integrates with flex output from `conf-scan.l`, libsepol policy version limits, libselinux policy root, semanage utilities, and direct commit configuration.

Risks: global parser state limits concurrency; duplicate string assignments must free previous values; some errors increment parse count but continue until abort boundaries. Test signals include default config when missing, validation errors for each option, command-block path requirements, and leak-free destroy after partial parses.
