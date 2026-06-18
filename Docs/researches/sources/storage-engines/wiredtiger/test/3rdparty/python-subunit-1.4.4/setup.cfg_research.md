# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/setup.cfg

## Purpose

This packaging configuration file customizes setuptools egg metadata generation for the vendored `python-subunit` package. It keeps generated egg-info version tags stable by disabling build and date suffixes.

## Important Configuration

- `[egg_info]` selects setuptools' egg-info command configuration.
- `tag_build =` is blank, so development/build tags are not appended to the package version.
- `tag_date = 0` disables adding the current date to generated version metadata.

## Control Flow, State, and Persistence

The file has no executable control flow. It is read by setuptools when `setup.py` invokes packaging commands that generate or update egg metadata. Its effects are persisted only in generated packaging artifacts such as egg-info metadata, not in runtime subunit behavior.

## Dependencies and Integration Points

The only integration point is setuptools/distutils configuration discovery. In this vendored tree it complements `setup.py`, which supplies the package metadata, dependencies, package list, and console entry points.

## Risks and Maintenance Signals

- Because the file suppresses dynamic build/date tags, downstream packaging expects `setup.py` or source metadata to provide the authoritative version.
- The blank `tag_build` value is meaningful; formatting cleanup that removes it could change generated egg-info behavior.
- This file does not constrain wheel metadata directly beyond the setuptools command behavior.

## Test Signals

There is no direct unit test for this file. Packaging smoke tests such as `python setup.py egg_info` or modern build invocations would reveal whether generated metadata remains stable.
