# sources/security-integrity/selinux/python/semanage/semanage

## Purpose
This executable Python entrypoint implements the `semanage` command-line interface for local SELinux policy management. It is almost entirely a parser and dispatcher layer: it defines subcommands, validates required and conflicting options, translates legacy import/export syntax, then delegates actual policy-store mutation and listing to record classes in `seobject.py`.

## Important APIs, types, and functions
- `CheckRole(argparse.Action)` validates `semanage user -R` role arguments through `sepolicy.get_all_roles()`, treating an unloadable policy as an empty valid-role set.
- `seParser` customizes `argparse.ArgumentParser.error()` so single-argument invocations show full help while normal parse errors show usage.
- `SetExportFile` and `SetImportFile` redirect `stdout`/`stdin` for `export -f` and `import -f`; `-` preserves the current stream.
- `object_dict` maps subcommand names to `seobject` record classes: login, SELinux user, port, module, interface, node, fcontext, boolean, permissive, dontaudit, ibpkey, and ibendport.
- `generate_custom_usage()` builds hand-written usage strings for complex subcommands.
- `handle_opts()` enforces action-specific conflicts and required arguments after argparse has accepted the command shape.
- `handleLogin`, `handleFcontext`, `handleUser`, `handlePort`, `handlePkey`, `handleIbendport`, `handleInterface`, `handleModule`, `handleNode`, `handleBoolean`, `handlePermissive`, `handleDontaudit`, `handleExport`, and `handleImport` are the command handlers.
- `mkargv()` tokenizes semanage import lines, preserving simple single- and double-quoted arguments.
- `createCommandParser()`, `make_io_args()`, `make_args()`, and `do_parser()` compose the CLI and run it.

## Control flow
Startup calls `do_parser()`, which creates the top-level parser, converts legacy `-o`/`-i` import/export invocations when needed, parses `sys.argv`, and invokes `args.func(args)`. Each setup function installs one subparser and sets a handler default. Handlers call `handle_opts()` to enforce semantic requirements, instantiate the matching `seobject` class with the parsed namespace, and call the method matching `args.action`.

`handleExport()` emits a delete-all command for every managed item, then walks each record class's `customized()` output to produce replayable local customizations. `handleImport()` starts a `seobject.semanageRecords` transaction, separates destructive lines containing `-d` or `-D` from the rest, applies destructive commands first through `importHelper()`, finishes, starts a second transaction, and applies all remaining commands. `importHelper()` reparses each imported command through a fresh command parser, so import shares the normal handler paths.

## State and persistence behavior
The file itself persists no SELinux policy data. It mutates process-level I/O by assigning `sys.stdout` and `sys.stdin` for import/export files. Persistent effects occur through `seobject` methods, which write libsemanage local customizations and commit transactions unless `--noreload` is set. Import mode relies on the class-level transaction state in `seobject.semanageRecords` to group multiple parsed commands.

## Dependencies and integration points
The script depends on Python `argparse`, `gettext`, `os`, `re`, `sys`, and `traceback`, plus local `seobject` and policy introspection from `sepolicy` for role validation. It is tightly coupled to method signatures in `seobject.py`; the parser's destination names (`login`, `seuser`, `range`, `type`, `proto`, `subnet_prefix`, `ibdev_name`, and so on) are passed directly to those methods. It also integrates with SELinux translations by using gettext domain `selinux-python`.

## Risks and edge cases
- Several `handle_opts()` dictionaries contain misspelled option names such as `localist`, `prototype`, and `subnet prefix`. Those entries do not match argparse destinations, so intended conflict checks are skipped for some actions.
- `handle_opts()` treats each dictionary entry as `(conflicts, required)`, but the `handleIbendport` `add` entry has a third tuple element that is ignored. This is harmless at runtime but signals uneven table maintenance.
- Import delete-command detection uses substring checks for `"-d"` and `"-D"` across the full line, so a value containing those strings can be classified as a deletion command.
- `mkargv()` is a small custom tokenizer, not shell-compatible quoting. It can mishandle escapes, malformed quotes, and complex import files.
- `SetExportFile` catches all exceptions and prints a traceback, exposing internal details but avoiding silent failure.
- The CLI layer is the only enforcement for many required parameters. Misspelled `handle_opts()` keys can let bad inputs reach libsemanage wrappers, where errors may be less user-friendly.

## Test signals
`test-semanage.py` exercises list, extract, import/export compatibility, fcontext, port, login, user, and boolean flows. It does not cover ibpkey, ibendport, module enable/disable/remove, dontaudit toggling, malformed import quoting, or the typoed option-conflict paths. Runtime testing requires SELinux enforcing mode and host tools such as `semanage`, `useradd`, and `userdel`.
