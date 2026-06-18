# sources/distributed-fs/tahoe-lafs/misc/coding_tools/check-interfaces.py

## Purpose

This legacy checker monkeypatches `zope.interface.implements` to verify class/interface conformance while importing Tahoe and Foolscap modules. It is intended to report all interface violations, not just the first.

## Important APIs, Types, and Functions

`strictly_implements` installs a class advisor that calls a forked `verifyClass` for classes in interesting modules. `check` monkeypatches `zi.implements`, walks a source directory, imports modules, and reports modules outside the interesting set. The forked verifier consists of `_verify`, `verifyClass`, `verifyObject`, and `_incompat`, using Zope interface method metadata.

## Control Flow

The script sets `sys.argv` to `['', '--help']` to reduce command-script side effects, imports every non-excluded `.py` module under `src` by default, warns for orphan `.pyc/.pyo`, handles Windows-only imports specially, and prints collected non-interesting module violations. On direct execution it calls `check()` then `os._exit(0)`.

## State, Dependencies, Integration, Risks, and Tests

State is global monkeypatching of `zope.interface.implements` and `_other_modules_with_violations`. Dependencies are old Zope interface APIs, Python 2 method attributes (`im_func`), and importability of the source tree. Risks include arbitrary import side effects, incompatibility with modern `zope.interface`, noisy false positives, and hard process exit. Tests should use small fixture packages with matching/mismatching interfaces and import failures, preferably in subprocess isolation.
