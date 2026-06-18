# sources/object-store/openstack-swift/swift/cli/ringcomposer.py

## Purpose
`ringcomposer.py` implements the experimental `swift-ring-composer` CLI for creating composite ring files from multiple component ring builder files. It can display composite builder metadata or compose and write a composite ring plus its composite builder metadata file.

## Important APIs, types, and functions
- `EXIT_SUCCESS` and `EXIT_ERROR` define CLI statuses.
- `WARNING` and `DESCRIPTION` contain operator-facing experimental-tool text.
- `_print_to_stderr()` and `_print_err()` centralize error output.
- `show(composite_builder, args)` prints the loaded composite builder as sorted, indented JSON.
- `compose(composite_builder, args)` creates or reuses a `CompositeRingBuilder`, calls `compose(builder_files, force=args.force, require_modified=True)`, saves the ring data to `--output`, then saves the composite builder file.
- `main(arguments=None)` parses the composite builder file plus `show` or `compose`, loads existing metadata when required, and exits with the subcommand status.

## Control flow
The CLI always prints the experimental warning to stderr before parsing arguments. `show` requires an existing composite builder file, loads it, and dumps metadata. `compose` permits a missing composite builder file by creating a fresh `CompositeRingBuilder`, then requires `--output` and accepts zero or more builder files plus `--force`. Composition, ring save, and builder save are separate try blocks so failure messages identify which stage failed.

## State and persistence behavior
`show` is read-only. `compose` writes two artifacts: the composed ring file at `args.output` and the composite builder metadata file at `args.composite_builder_file`. With `require_modified=True`, composition can refuse to rewrite an unchanged composite unless `--force` is appropriate at the `CompositeRingBuilder` layer.

## Dependencies and integration points
The file depends almost entirely on `swift.common.ring.composite_builder.CompositeRingBuilder` and ring data serialization returned by its `compose()` method. It complements but is distinct from `swift-ring-builder`; the docstring explicitly warns that generated composite rings do not have a normal builder file and should not be managed through a reconstructed temporary builder.

## Risks and edge cases
The code uses broad `except Exception` handlers to convert all compose/load/save failures into status 2, which is useful operationally but hides exception type detail. `main()` assumes a subparser sets `args.func`; invoking without a subcommand depends on argparse behavior and may produce a less curated error. Empty `builder_files` is syntactically allowed and delegated to `CompositeRingBuilder.compose()` for validation. The tool is explicitly experimental, so CLI and behavior may be unstable.

## Test signals
Tests should exercise missing and existing composite builder files, `show` JSON output, compose success write order, load/compose/ring-save/builder-save failures, `--force` propagation, no-subcommand parser behavior, and the exit status contract.
