# sources/sync-backup/git-crypt/parse_options.cpp

Purpose: small option parser for git-crypt subcommands supporting long options, `--name=value`, `--name value`, clustered short flags, short options with attached values, and `--` termination.

Important APIs/types/functions: `find_option` and `parse_options`.

Control flow: `parse_options` walks argv until a non-option or `--`. Long options split at `=`, look up a declared `Option_def`, set boolean flags or consume values, and reject unexpected/missing values. Short option clusters process one character at a time; boolean flags continue through the cluster, while value options consume the rest of the cluster or the next argv and then stop the cluster.

State/persistence behavior: mutates caller-provided bools or `const char**` value slots. It returns the index of the first positional argument. No persistent state.

Dependencies/integration: used by command handlers and `git-crypt.cpp` catches `Option_error` to print command help.

Risks/test signals: parser has no support for optional values or combined long abbreviations. Tests should cover `-abc`, `-kname`, `-k name`, `--key-name=name`, `--key-name name`, `--`, invalid options, missing values, and value supplied to flag-only options.
