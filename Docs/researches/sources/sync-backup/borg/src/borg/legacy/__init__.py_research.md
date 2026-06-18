# sources/sync-backup/borg/src/borg/legacy/__init__.py

## Purpose
Documents the legacy package as Borg's Borg 1.x compatibility layer for `borg transfer --from-borg1` and serving v1 clients.

## Important APIs, Types, And Functions
This package initializer exports no runtime API. Its module docstring explains the package boundary and planned removability when Borg 1.x support is dropped.

## Control Flow
No executable control flow beyond module import.

## State And Persistence
No state and no persistence.

## Dependencies And Integration Points
The package contains legacy archive, crypto, hashindex, repository, remote, repo object, helper, and upgrade code. Importers use submodules directly.

## Risks And Edge Cases
Because it is documentation-only, risk is low. The main maintenance risk is stale package-level documentation if legacy support scope changes.

## Test Signals
Coverage comes from submodule tests such as legacy archive/helper/upgrade/repository tests rather than this initializer.
