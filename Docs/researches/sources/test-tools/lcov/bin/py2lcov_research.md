# sources/test-tools/lcov/bin/py2lcov Research

Purpose: `py2lcov` is an executable Python front end that converts Coverage.py data files, or deprecated intermediate XML files, into LCOV `.info` format through the shared `xml2lcovutil.ProcessFile` implementation.

Important APIs and functions: `main()` owns all behavior. It builds an `argparse.ArgumentParser`, exposes LCOV-oriented options (`--output`, `--test-name`, `--exclude`, `--version-script`, `--checksum`, `--no-functions`, `--keep-going`) plus Coverage.py command selection through `--cmd` or `COVERAGE_COMMAND`, marks `args.isPython = True`, and delegates conversion to `ProcessFile`.

Control flow: command-line parsing first folds deprecated `--input` into positional inputs. If no inputs are supplied, it falls back to `COVERAGE_FILE`; otherwise it exits. For each input, `.xml` files are processed directly. Non-XML files are treated as Coverage.py data: the script chooses a temporary sibling XML filename, runs `[coverage-command, "xml", "-o", xml]` with `COVERAGE_FILE` set to that input, processes the generated XML, and deletes it. `ProcessFile.close()` finalizes output and may run `lcov` for Perl-module version-script handling.

State and persistence: persistent outputs are the selected LCOV info file and transient generated XML files that are unlinked after processing. Runtime state is held in parsed args, environment variables, and the `ProcessFile` object.

Dependencies and integration: it integrates Coverage.py XML extraction with the LCOV converter utility. It expects the configured coverage executable to support `coverage xml`; old Coverage.py data-file handling is documented through environment fallback.

Risks: temporary XML deletion is skipped if processing aborts before `os.unlink`. `subprocess.run(..., stdout=True, stderr=True)` uses booleans rather than capture constants, so output capture is not meaningful. Function derivation can make merged data inconsistent when mixed with `--no-functions`. Import path assumes `xml2lcovutil.py` is beside the script.

Test signals: cover direct XML input, data-file input conversion, existing temporary XML suffix selection, `COVERAGE_FILE` fallback, failing coverage command with and without `--keep-going`, `--no-functions`, checksum mode, and version-script post-processing.
