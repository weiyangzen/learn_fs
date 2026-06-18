# Research: sources/user-network-fs/mergerfs/vendored/CLI11/CLI11.hpp

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009673`: lines 1-6823, `Docs/researches/chunks/subset-b-009673_research.md`
- `subset-b-009674`: lines 6824-12216, `Docs/researches/chunks/subset-b-009674_research.md`

## Chunk Research

### subset-b-009673: lines 1-6823

# sources/user-network-fs/mergerfs/vendored/CLI11/CLI11.hpp lines 1-6823

## Scope

This chunk covers the front portion of the vendored CLI11 single-header library, version 2.6.2. It starts at the generated header metadata and standard/platform includes, then defines the `CLI` namespace support layer through most of `CLI::Option`. The range ends inside `Option::_validate_results`, before the rest of option reduction, parsing, `App`, config serialization, and formatter implementations that appear later in the header.

This is third-party command-line parsing infrastructure used by mergerfs rather than mergerfs-specific filesystem logic. The code is header-only unless `CLI11_COMPILE` is defined, in which case `CLI11_INLINE` changes linkage expectations.

## Purpose

The covered code provides the foundation for CLI11's public API:

- Compiler/platform feature detection for C++14/17/20/23/26, RTTI, `<filesystem>`, `<codecvt>`, Windows argument decoding, and inline/module linkage.
- UTF-8/wide-string conversion helpers for Windows and non-Windows builds.
- String parsing helpers for command lines, config tokens, quoted strings, binary-escaped strings, option-name splitting, and paragraph formatting.
- The CLI11 error hierarchy and typed exit codes.
- Template metaprogramming that classifies option target types, generates help type names, converts strings to typed values, and fills tuples/containers/wrappers.
- Config item abstractions and configurable TOML/INI parsing front matter.
- Validators and transformers used by options, including file/path checks, type/range checks, member-set validation, string-to-value mapping, unit conversion, IPv4 validation, and optional permission checks.
- Formatter interfaces and the beginning of option registration/state APIs.
- `OptionBase`, `OptionDefaults`, and most of `Option`, including names, expected counts, validators, needs/excludes, environment binding, defaults, result storage, callback execution, and the beginning of result validation.

## Important APIs And Types

Public and integration-facing items in this chunk include:

- Version macros: `CLI11_VERSION_MAJOR`, `CLI11_VERSION_MINOR`, `CLI11_VERSION_PATCH`, and `CLI11_VERSION`.
- Encoding helpers: `CLI::narrow`, `CLI::widen`, and, when filesystem is available, `CLI::to_path`.
- Windows command-line helper: `detail::compute_win32_argv`, which uses `CommandLineToArgvW(GetCommandLineW())` and converts wide argv values to UTF-8 strings.
- Generic string utilities in `CLI::detail`: `split`, `join`, `rjoin`, `trim` variants, `remove_quotes`, `fix_newlines`, `valid_name_string`, `find_member`, `split_up`, `process_quoted_string`, `binary_escape_string`, `extract_binary_string`, and `streamOutAsParagraph`.
- Error classes: `Error`, `ConstructionError`, `IncorrectConstruction`, `BadNameString`, `OptionAlreadyAdded`, `ParseError`, `Success`, `CallForHelp`, `CallForAllHelp`, `CallForVersion`, `RuntimeError`, `FileError`, `ConversionError`, `ValidationError`, `RequiredError`, `ArgumentMismatch`, `RequiresError`, `ExcludesError`, `ExtrasError`, `ConfigError`, `InvalidError`, `HorribleError`, and `OptionNotFound`.
- Type traits and conversion helpers: `enable_if_t`, `void_t`, `conditional_t`, `is_mutable_container`, `is_tuple_like`, `type_count`, `type_count_min`, `expected_count`, `classify_object`, `type_name`, `lexical_cast`, `lexical_assign`, `lexical_conversion`, `tuple_conversion`, and `sum_string_vector`.
- Option-name helpers: `split_short`, `split_long`, `split_windows_style`, `split_names`, `get_default_flag_values`, and `get_names`.
- Config APIs: `ConfigItem`, abstract `Config`, `ConfigBase`, alias `ConfigTOML`, and `ConfigINI`.
- Validator APIs: `Validator`, `CustomValidator`, built-in global validators such as `ExistingFile`, `ExistingDirectory`, `ExistingPath`, `NonexistentPath`, `EscapedString`, `Number`, `ValidIPV4`, `NonNegativeNumber`, `PositiveNumber`, and classes `FileOnDefaultPath`, `Range`, `Bound`, `IsMember`, `Transformer`, `CheckedTransformer`, `AsNumberWithUnit`, and `AsSizeValue`.
- Formatting interfaces: `AppFormatMode`, `FormatterBase`, `FormatterLambda`, and declaration-heavy `Formatter`.
- Option APIs: `results_t`, `callback_t`, `Option_p`, `Validator_p`, `MultiOptionPolicy`, `CallbackPriority`, `OptionBase<CRTP>`, `OptionDefaults`, and `Option`.

`Option` is the central stateful type in this range. It stores short names, long names, default flag values, one positional name, environment variable name, help strings, dynamic type/default string functions, type arity, expected count range, validators, dependency/exclusion links, parent `App *`, callback, raw results, reduced results, option parse state, and behavior flags such as `allow_extra_args_`, `flag_like_`, `inject_separator_`, `trigger_on_result_`, and `force_callback_`.

## Control Flow

Header setup is mostly preprocessor control flow. Feature macros select C++ feature levels, filesystem support, codecvt support, RTTI behavior, diagnostics pragmas, Windows headers, and whether path checks use `std::filesystem` or `stat`.

String conversion routes through `narrow_impl` and `widen_impl`. With codecvt available, it uses `std::wstring_convert`; otherwise it temporarily switches the process locale to a UTF-8-capable locale, uses `wcsrtombs`/`mbsrtowcs`, and restores the old locale with a scope guard. This fallback is process-global because C locale mutation is global.

Token parsing helpers are layered:

1. `split_names` splits comma-separated declarations.
2. `get_default_flag_values` extracts flag aliases with `{default}` or `!` false-style markers.
3. `get_names` validates and categorizes names into short, long, and positional forms, throwing `BadNameString` for malformed or reserved names.
4. `split_short`, `split_long`, and `split_windows_style` recognize runtime command-line tokens.
5. `split_up`, `close_sequence`, and quote/escape helpers preserve quoted/bracketed groups and unescape JSON-like sequences.

Type conversion control flow is compile-time selected with SFINAE. `classify_object` chooses a category, then `lexical_cast` overloads parse integers, unsigned integers, chars, bools, floating-point values, complex numbers, strings, wide strings, enums, wrappers, constructible numeric classes, and stream-readable fallback types. `lexical_conversion` then scales one-string conversion up to tuples, containers, vectors of tuple-like entries, complex values, and wrapper types. Container conversion uses `detail::is_separator` markers to split variable-sized elements.

Validator control flow is uniform: a validator owns a `std::function<std::string(std::string &)>` that returns an empty string on success or an error message on failure. `Validator::operator&` runs both functions and combines errors; `operator|` succeeds if either validator succeeds; `operator!` fails when the wrapped validator succeeds. Transforming validators mutate the input string, while `check()` marks validators non-modifying before attaching them to an option.

`Option` setup and execution flow in this chunk is:

1. The private constructor parses the option declaration into `snames_`, `lnames_`, and `pname_`.
2. `OptionBase::copy_to` copies default option settings into concrete options.
3. `expected()` and `type_size()` configure how many option occurrences and raw strings are expected.
4. `check()`, `transform()`, and `each()` append or prepend validators.
5. `needs()` and `excludes()` build dependency and mutual-exclusion sets; `excludes()` also inserts the reverse relationship.
6. `ignore_case()` and `ignore_underscore()` temporarily enable matching changes, scan parent app options for conflicts, and roll back on conflict.
7. `add_result()` appends raw parsed strings through `_add_result()` and resets state to `parsing`.
8. `run_callback()` validates raw results if needed, reduces them if needed, picks reduced or raw results, invokes the callback, clears forced default results when appropriate, and throws `ConversionError` if the callback reports failure.
9. `results<T>()` obtains reduced/validated results or default-derived results, stores them in `proc_results_` when needed to stabilize view-like outputs, and uses `detail::lexical_conversion<T, T>`.
10. `_validate_results()` begins validator application. In this chunk it handles multi-value options by computing an index modulo `type_size_max_`, resets indexes on separator entries for variable-sized chunks, and creates negative indexes for earlier values when `TakeLast` or `Reverse` policies mean only later values are relevant. The source range stops before the single-value loop body and before `_reduce_results()`.

## State And Persistence Behavior

Most state is in memory and owned by parser objects:

- `ConfigBase` stores parse/emit configuration such as comment character, array delimiters, quote characters, parent separator, maximum nesting layers, duplicate-field behavior, selected section, and section index.
- `Validator` stores a description function, operation function, name, application index, active flag, and non-modifying flag. Validators attached to options are `std::shared_ptr<Validator>`.
- `OptionBase` stores option defaults and behavior shared by `OptionDefaults` and `Option`.
- `Option` stores parse results in `results_`, caches reduced results in mutable `proc_results_`, and tracks lifecycle with `current_option_state_`.

There is no durable persistence in this chunk, but it does include I/O boundaries:

- `Config::from_file()` opens a config file through `std::ifstream`, using `std::filesystem::path` conversion when available.
- Path validators inspect the filesystem with `std::filesystem::status` or `stat`/`_stat64`.
- `get_environment_value()` reads process environment variables via `_dupenv_s` on MSVC or `std::getenv` elsewhere.
- `split_program_name()` probes candidate command prefixes with `check_path()` to infer a program name.

Static local state appears in `AsSizeValue::get_mapping`, which caches size-unit maps for base-1000 and base-1024 interpretations. Global constant validator objects are initialized at program startup or module load according to C++ static initialization rules.

## Dependencies And Integration Points

This header depends only on the C++ standard library and narrow platform APIs:

- Standard headers for algorithms, streams, containers, type traits, locale, conversion, exceptions, and file I/O.
- Optional `<filesystem>` for path validation and config path opening.
- Optional `<codecvt>` for UTF-8/wide conversion on pre-C++26-capable builds.
- POSIX `stat` through `<sys/stat.h>` and `<sys/types.h>` when filesystem is unavailable.
- Windows APIs and headers for native argv decoding and filesystem checks on Windows builds.

Within mergerfs, this vendored header is an integration dependency for command-line parsing. Code that includes it can build a `CLI::App` in later parts of the header, register options, attach validators, read configuration files, consult environment variables, and receive typed callback values. This chunk supplies the low-level pieces those later `App` APIs rely on.

Important internal integration points include:

- `App` is forward-declared and granted friendship by `OptionBase`/`Option`; later `App` code constructs options, owns `Option_p`, runs parsing, calls private validation/reduction helpers, and inspects option internals.
- `ConfigBase` is a friend of `Option` and later maps `ConfigItem` values into options.
- `Formatter` methods are declared here but implemented later; they call option getters such as `get_name`, `get_type_name`, `get_default_str`, and relationship getters.
- `Option`'s `ignore_case` and `ignore_underscore` methods assume the parent object exposes `options_` and `get_option_no_throw`, so they are tightly coupled to the later `App` definition.
- Validators use the same `lexical_cast` and `type_name` infrastructure as option callbacks, making help text, validation, and final conversion consistent.

## Risks And Maintenance Notes

- This is a vendored generated single header. Local edits can diverge from upstream CLI11 and are hard to review because declarations and implementations are interleaved across thousands of lines.
- The codecvt-disabled fallback mutates the process C locale around conversions. The scope guard restores it, but `setlocale` is process-global and can be problematic in multithreaded code.
- Many behaviors are selected by compiler and platform macros. A path validated with `std::filesystem` on one build may go through `stat` on another; Windows also has separate wide/narrow argument handling.
- Template dispatch is broad and subtle. New target types can accidentally classify as strings, wrappers, containers, tuples, or constructible numeric classes, changing how CLI values are split and converted.
- `lexical_cast` accepts numeric separators, base prefixes, boolean synonyms, complex suffixes, and stream fallback. These convenience paths should be covered when changing conversion rules because they affect all options and validators.
- `sum_string_vector` falls back from numeric addition to string concatenation if any element is not numeric/flag-like. This underpins `MultiOptionPolicy::Sum` later and can surprise callers expecting strict numeric behavior.
- Validators may mutate input unless attached through `check()`, which forces `non_modifying()`. Ordering matters because `transform()` inserts validators at the beginning, before later checks.
- `Option::default_val()` temporarily clears and restores `results_` and `current_option_state_` while validating or running callbacks for defaults. Exceptions must leave the old option state intact.
- `excludes()` creates symmetric links but `remove_excludes()` removes only from the current option's set in this chunk. Callers relying on symmetry need to understand later `App` cleanup behavior.
- The range ends mid-`Option::_validate_results`; final validation and reduction semantics are completed outside this chunk.

## Test Signals

Useful validation for this chunk is mostly compile-time plus focused behavioral tests:

- Compile a mergerfs target that includes `sources/user-network-fs/mergerfs/vendored/CLI11/CLI11.hpp` under the repository's normal compiler flags.
- Add or run CLI tests that exercise short, long, positional, default-flag, and Windows-style name splitting.
- Verify malformed declarations throw the expected construction errors: reserved names (`-`, `--`, `++`), one-dash long names when non-standard names are disabled, duplicate positional names, and invalid characters.
- Test string parsing with quoted strings, escaped quotes, `\u`/`\U` escapes, binary escaped strings, bracketed values, and delimiter-separated vectors.
- Test numeric conversion for decimal, hex, octal `0o`, binary `0b`, grouped numbers, unsigned overflow, booleans (`true`, `false`, `on`, `off`, `yes`, `no`, `+`, `-`), floating values, complex values, enums, tuples, and containers.
- Test validators: existing/non-existing file/path, `Range`, `Bound`, `IsMember` with ignore filters, `Transformer`, `CheckedTransformer`, `AsNumberWithUnit`, `AsSizeValue`, and `ValidIPV4`.
- Test option state transitions by adding results, calling `reduced_results()`, calling `results<T>()`, setting `default_val()`, forcing callbacks, and using `trigger_on_parse`.
- Test conflict detection for `ignore_case()` and `ignore_underscore()` against sibling options in a parent `App`.
- On Windows, verify `compute_win32_argv`, wide-string `parse` paths, and `to_path` preserve non-ASCII arguments and file paths.

### subset-b-009674: lines 6824-12216

# `sources/user-network-fs/mergerfs/vendored/CLI11/CLI11.hpp` lines 6824-12216

## Purpose

This chunk contains the central inline implementation and public surface for CLI11's command-line application model. It starts by finishing `Option` result reduction, validation, and string-to-result expansion, then defines the `CLI11_PARSE` convenience macro, `App` and `Option_group`, the command/subcommand parse engine, config-file read/write helpers, failure-message helpers, and the default help `Formatter`.

Within the vendored mergerfs tree this is third-party CLI parsing infrastructure. Local mergerfs code uses it indirectly by including `CLI11.hpp` and building `CLI::App` instances with options, flags, subcommands, config files, environment fallbacks, validators, and callbacks. The covered range is behavioral code, not merely declarations: it owns the parse state machine and the ordering rules that decide when callbacks, help/version exits, config files, environment variables, requirements, and extras are processed.

## Important APIs, Types, and Functions

The `Option` helpers at the start of the chunk are internal but shape nearly every option parse result:

- `Option::_reduce_results(results_t &out, const results_t &original)` applies `MultiOptionPolicy`. `TakeLast`, `Reverse`, and `TakeFirst` trim to the expected item count; `Join` joins original strings with the configured delimiter or newline; `Sum` numeric-sums string values; `Throw` enforces min/max counts. It also handles the special config empty-container sentinel `{}` plus `%%`.
- `Option::_validate(std::string &result, int index)` runs validators whose application index is either global `-1` or matches the input index. It returns the first error string, converting thrown `ValidationError` to text.
- `Option::_add_result(std::string &&result, std::vector<std::string> &res)` expands parsed strings into result elements. It recognizes escaped bracket vectors of the form `[[...]]` with duplicated characters, bracketed vector strings split by comma, and delimiter-separated values.

`detail::Classifier` is the parse-token category enum used by `App::_recognize` and `App::_parse_single`: `NONE`, `POSITIONAL_MARK`, `SHORT`, `LONG`, `WINDOWS_STYLE`, `SUBCOMMAND`, and `SUBCOMMAND_TERMINATOR`.

The extras and prefix enums drive unknown-argument behavior:

- `ExtrasMode` supports hard errors, immediate errors, ignore, capture, and two "assume following args" modes.
- `ConfigExtrasMode` / `config_extras_mode` decide whether unknown config keys error, ignore, ignore all not-configurable keys, or are captured into `missing_`.
- `PrefixCommandMode` controls command-wrapper behavior where an unrecognized token stops CLI11 parsing and leaves the rest for a downstream executable.

`CLI::App` is the core command/subcommand object. Its state includes:

- Basic identity and callback fields: `name_`, `description_`, `has_automatic_name_`, `required_`, `disabled_`, `pre_parse_callback_`, `parse_complete_callback_`, and `final_callback_`.
- Option storage and defaults: `option_defaults_`, `options_`, `help_ptr_`, `help_all_ptr_`, `version_ptr_`, and `config_ptr_`.
- Parse state: `missing_`, `parse_order_`, `parsed_subcommands_`, `parsed_`, and requirement/exclusion sets for options and subcommands.
- Subcommand behavior: `subcommands_`, `ignore_case_`, `ignore_underscore_`, `fallthrough_`, `subcommand_fallthrough_`, `allow_windows_style_options_`, `positionals_at_end_`, `configurable_`, `validate_positionals_`, `validate_optional_arguments_`, `silent_`, `allow_non_standard_options_`, and `allow_prefix_matching_`.
- Formatting and config dependencies: `formatter_` defaults to `Formatter`, and `config_formatter_` defaults to `ConfigTOML`.

Public `App` APIs in this range include callback setup, parser mode setters, option and flag creation, config option setup, subcommand creation/removal, option groups, requirements/exclusions, help and version generation, accessors, `parse(...)` overloads for argc/argv, strings, vectors, wide strings, and streams, and `exit(...)` for converting `ParseError` subclasses into output and exit codes.

The typed `add_option` templates convert CLI string results into user variables using `detail::lexical_conversion`, derive type names/counts from type traits, install default-string capture callbacks, and configure expected argument counts. Flag APIs route through `_add_flag_internal`, which strips default flag-value annotations from names when present, rejects positional flags, sets `MultiOptionPolicy::TakeLast`, expected count zero, and non-required status. Integral counting flags use `MultiOptionPolicy::Sum`.

`Option_group` subclasses `App` with an empty app name and group label. It lets callers move existing options and subcommands under a group while preserving ownership in the underlying `App_p` vectors. Groups whose names are empty or start with `+` remove inherited help flags and participate specially in option lookup/help expansion.

Helper APIs `TriggerOn`, `TriggerOff`, `deprecate_option`, and `retire_option` mutate app/option behavior. Trigger helpers install preparse callbacks that enable or disable other apps. Deprecation and retirement are implemented by adding validators that print warnings to `std::cout`; retirement replaces or creates an inert option with type/default text `"RETIRED"`.

`FailureMessage::simple` and `FailureMessage::help` are the default error formatting hooks. `simple` emits the error text plus a help flag suggestion; `help` emits an `ERROR:` header and full help output.

Config helpers implement both parsing and serialization:

- `detail::convert_arg_for_ini` quotes, escapes, or preserves strings based on whether they look like booleans, numbers, hex/octal/binary literals, printable text, binary data, or long multiline values.
- `detail::ini_join` joins vector results using config array delimiters.
- `detail::generate_parents`, `detail::checkParentSegments`, `detail::hasMLString`, and `detail::find_matching_config` maintain nested section parent paths and duplicate-key merging.
- `ConfigBase::from_config` parses INI/TOML-like streams into `ConfigItem` entries.
- `ConfigBase::to_config` serializes current app/option/subcommand state back to config text.

`Formatter` methods at the end generate default help text: descriptions, usage, positionals, option groups, subcommand groups, expanded subcommand help, option names/options/descriptions, and positional usage fragments.

## Control Flow

Top-level `parse` setup is consistent across overloads. The argc/argv overload records an automatic app name from `argv[0]` if needed, reverses command-line arguments into a vector, and calls `parse(vector)`. String parsing optionally extracts a program name, escapes quoted values after `=` or Windows-style `:`, splits shell-like text, removes quotes, reverses arguments, and calls `parse(vector)`.

`parse(vector)` and `parse(vector&&)` clear previous parse data if needed, temporarily mark `parsed_` so cleanup happens if validation/configuration throws, then run `_validate()`, `_configure()`, detach the root from any parent, reset `parsed_`, and enter `_parse`. `parse_from_stream` skips command-token parsing and feeds config items directly into `_parse_config`.

The command-token state machine is:

1. `_parse` increments parse counts for the current app and nameless groups, triggers preparse once, and loops while args remain.
2. `_parse_single` classifies the next token with `_recognize`, then dispatches to positional mark handling, subcommand parsing, option parsing, or positional parsing.
3. `_recognize` checks `--`, valid subcommands, long options, short options, numeric-looking short-token exceptions, Windows-style options, `++` subcommand terminators, and dotted subcommand notation.
4. `_parse_subcommand` resolves the subcommand, supports dotted notation, records non-silent parsed subcommands, recurses into the child app, and propagates parsed-subcommand state through intermediate parents.
5. `_parse_arg` splits long/short/Windows tokens, finds a local option, searches nameless subcommands, supports non-standard short names, supports dotted subcommand option notation, falls through to parents when enabled, captures unknown options into `missing_`, or consumes option values according to min/max/type-size rules.
6. `_parse_positional` assigns a positional to the first eligible positional option, optionally validating before assignment. If no local positional can consume it, it tries nameless subcommands, fallthrough parents, repeated subcommands, subcommand fallthrough, extras handling, and prefix-command capture.

Option value collection is sensitive to arity. `_parse_arg` handles flag-like zero-argument options through `get_flag_value`, `--long=value`, short rest values such as `-Trest`, required minimum positional values, optional values while the next token is `NONE`, `--` ending an unlimited list, flag defaults when optional values are omitted, partial tuple/type errors, and `trigger_on_parse` callbacks. It leaves unused short-token rest back on the arg stack as a new short option.

After token parsing, root `_parse` runs `_process`, then `_process_extras`. `_process` deliberately stages callbacks and help checks by `CallbackPriority`: `FirstPreHelp`, help at `First`, `First`, config/env processing, `PreRequirementsCheckPreHelp`, help at `PreRequirementsCheck`, requirements, `NormalPreHelp`, help at `Normal`, `Normal`, delayed config-file exception rethrow, `LastPreHelp`, help at `Last`, and `Last`. This gives help/version and callback priorities predictable precedence over config-file failures and requirement checks.

For subcommands with `parse_complete_callback_`, `_parse` runs a reduced process pipeline immediately at subcommand parse completion, including env processing and requirements, then calls `run_callback(false, true)` to suppress the final callback until the main callback pass.

Config parse flow starts with `ConfigBase::from_config`, which scans lines, ignores short/comment/multiline-comment blocks, opens and closes sections with synthetic `++` and `--` items, handles multiline quoted values, arrays, whitespace/comma splitting, quoted string unescaping, parent-path extraction, duplicate merging with `%%` separators, maximum-layer filtering, and optional config-section filtering. `App::_parse_config` feeds each `ConfigItem` through `_parse_single_config`, erroring on unknown keys only in `ConfigExtrasMode::Error`.

`_parse_single_config` descends through `item.parents`, handles `++` section-open by incrementing parsed/configurable subcommands and recording them in the parent, handles `--` section-close with parse-complete callbacks, resolves configurable options by long, short, positional, or predicate search, captures unknown config extras when enabled, converts flag-like config items through `_add_flag_like_result`, and otherwise adds inputs then runs the option callback.

Help flow starts in `App::exit` or `_process_help_flags`. A help flag throws `CallForHelp`, all-help throws `CallForAllHelp`, and version throws `CallForVersion`. `exit` routes those to `help()`, all-help `help("", AppFormatMode::All)`, or `e.what()`. `App::help` delegates to the last selected subcommand so nested help describes the active leaf command; otherwise it calls the configured formatter.

## State and Persistence Behavior

Most state is process-local parse state inside `App` and `Option` objects. `clear()` resets `parsed_`, `pre_parse_called_`, `missing_`, `parsed_subcommands_`, `parse_order_`, every option, and all subcommands. `_configure()` reapplies startup enable/disable defaults, clears automatically generated names for child apps, disables fallthrough/prefix mode on nameless groups to avoid loops, and restores parent pointers before each parse.

`App` owns options and subcommands by `std::shared_ptr` (`Option_p` and `App_p`) but exposes raw pointers for user-facing APIs. Removal routines clean dependency links before erasing owning pointers. `_move_option` transfers ownership from a parent app to a subcommand/option group, rejecting help and config options.

Persistent external state is limited to explicit config-file and environment interactions. `_process_config_file` checks path type and reads config files through the configured `Config` object. `_process_env` reads environment variables for options that were not set by command line/config. `ConfigBase::to_config` produces a string representation but does not write files itself. `ensure_utf8` on Windows stores normalized argument strings and a parallel `char *` view inside the `App`; on non-Windows it returns the original pointer unchanged.

Callback helpers and deprecation/retirement warnings write to `std::cout`, while parse exit formatting writes to caller-provided `out`/`err` streams. No network, database, or long-lived cache behavior exists in this chunk.

## Dependencies

This code depends heavily on the earlier parts of the same header:

- `Option`, `OptionDefaults`, `FormatterBase`, `Formatter`, `FormatterLambda`, `Config`, `ConfigBase`, `ConfigTOML`, `ConfigItem`, `Validator`, `results_t`, `callback_t`, `MultiOptionPolicy`, `CallbackPriority`, and `AppFormatMode`.
- Error types such as `ParseError`, `ValidationError`, `ArgumentMismatch`, `ConversionError`, `RequiredError`, `RequiresError`, `ExcludesError`, `ExtrasError`, `ConfigError`, `FileError`, `IncorrectConstruction`, `OptionAlreadyAdded`, `OptionNotFound`, `CallForHelp`, `CallForAllHelp`, `CallForVersion`, `RuntimeError`, `InvalidError`, and `HorribleError`.
- `detail` utilities for string splitting, quoting, lexical conversion, flag values, path checks, environment reads, Windows narrowing/normalization, name validation, joins, paragraph formatting, binary escaping, and expected-count/type-count traits.

Standard-library dependencies include strings, vectors, sets, shared pointers, function objects, streams/stringstreams, algorithms, locale/ctype checks, exceptions, and iostreams. `_WIN32` gates Windows UTF-8 argv normalization and the default for Windows-style `/option` parsing.

## Integration Points

The primary integration contract is the public `CLI::App` API used by mergerfs command setup code. Callers create an `App`, add typed options/flags/subcommands, set config/env/help/version behavior, call `parse`, and then read bound variables or execute callbacks.

Config integration is two-way. Apps can set a config option with `set_config`; during processing, config file names may come from CLI arguments, default values, or an environment variable on the config option. Config items are parsed into the same option result/callback pipeline as command-line values. `config_to_str` serializes current values using `ConfigBase::to_config`, including configurable subcommands and option groups.

Help integration is formatter-pluggable. `App::formatter` accepts a `FormatterBase`, and `formatter_fn` wraps a callback in `FormatterLambda`. The default formatter queries `App` and `Option` getters, so changing option metadata affects usage/help output without changing formatter code.

Subcommand integration is hierarchical. Parent settings marked inheritable are copied in the child constructor, including option defaults, failure message, extras modes, prefix mode, immediate callback mode, case/underscore matching, fallthrough, validators for positionals/optional arguments, configurability, Windows-style options, group, usage/footer, formatter/config formatter, max subcommands, and prefix matching.

Testing integration is explicit through `detail::AppFriend`, which exposes protected parse helpers and fallthrough-parent lookup for tests while keeping those methods hidden from the normal public API.

## Risks and Edge Cases

- Pointer lifetime is easy to misuse. User-facing APIs return raw `Option *` and `App *` backed by vectors of `shared_ptr`; `remove_option`, `remove_subcommand`, and `_move_option` can invalidate previously saved raw pointers.
- Many behaviors depend on reversed argument vectors. External callers using `parse(std::vector<std::string> &args)` must pass a reversed vector as documented; otherwise parse order and leftovers are wrong.
- Dotted subcommand notation mutates the argument stack and has rollback paths. Bugs here can misroute options between parent and child apps, especially with short-option rest splitting.
- `ignore_case`, `ignore_underscore`, aliases, option groups, non-standard options, and prefix matching all widen match equivalence. The code performs conflict checks, but these settings can still create ambiguous UX, especially across nameless option groups and fallthrough parents.
- Config parsing is permissive and feature-rich: multiline strings, arrays, duplicate fields, section nesting, `++`/`--` synthetic items, `%%` separators, and quote rules all interact. Small changes to escaping or duplicate merging can change callbacks and option counts.
- The `{}` plus `%%` sentinel is a special empty-container escape used in option reduction/config output. Treating it as ordinary user data can make empty vectors and literal `"{}"` indistinguishable unless the guard paths stay intact.
- `deprecate_option` and `retire_option` warnings print directly to `std::cout` from validators. Applications that expect all diagnostics on `stderr` or caller-provided streams may get surprising output.
- Config-file `FileError` is intentionally delayed so callbacks/help/requirements can win. Tests that assert exact exception ordering need to account for this staged rethrow.
- `App::version()` temporarily clears and re-adds results on the version option to force the version callback, so custom callbacks with side effects could observe a synthetic state.
- `TriggerOn` and `TriggerOff` replace the target app's startup mode and the trigger app's preparse callback. A later `preparse_callback` assignment can overwrite trigger behavior because only one callback is stored.
- `ConfigBase::from_config` silently skips entries deeper than `maximumLayers` and short lines under three characters. That is intentional, but malformed or minimal config keys can disappear rather than error.

## Test Signals

Useful test coverage for this chunk should exercise behavior rather than only compiling the header:

- Parse a simple `App` with typed options, flags, counting flags, default flag values, repeated options under every `MultiOptionPolicy`, delimiter-split values, and validators with application indexes.
- Verify option arity errors: too few, too many, partial tuple/type, optional values stopping before required positionals, unlimited vector termination with `--`, and `positionals_at_end` extras errors.
- Cover subcommands with aliases, case/underscore-insensitive matching, prefix matching, silent subcommands, repeated subcommands, `require_subcommand`, named and nameless option groups, fallthrough, and subcommand fallthrough.
- Assert callback priority ordering with help/version/config/env/requirements. Include delayed config-file failure where a help flag or higher-priority callback wins.
- Test `parse_complete_callback_` and `immediate_callback_` on nested subcommands, including the clear-and-reparse behavior in `_trigger_pre_parse`.
- Exercise config files with nested sections, configurable subcommands, `++` and `--` section markers, unknown keys under every `ConfigExtrasMode`, duplicate fields, arrays, multiline quoted strings, literal `"{}"`, empty containers, and environment-sourced config file names.
- Round-trip `config_to_str` for normal options, flag aliases/default flag values, `Join`, `Sum`, `Reverse`, default values, required placeholders, option descriptions, option groups, configurable subcommands, and key names requiring quotes.
- Check help output for usage, positionals, grouped options, hidden help flags in subcommand mode, all-help expanded subcommands, aliases on display names, required labels, env/needs/excludes annotations, custom usage/footer callbacks, and paragraph formatting.
- Verify `remove_option`, `remove_subcommand`, `remove_needs`, `remove_excludes`, and `Option_group::add_option/add_subcommand` clean links and preserve ownership without leaving dangling dependency relationships.
