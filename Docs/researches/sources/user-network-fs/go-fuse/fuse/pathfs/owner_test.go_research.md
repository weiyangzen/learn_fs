# `sources/user-network-fs/go-fuse/fuse/pathfs/owner_test.go`

## Purpose
Tests owner override behavior when pathfs attributes flow through nodefs mount options.

## Important APIs, Types, And Functions
Defines `ownerFs`, `_RANDOM_OWNER`, `setupOwnerTest`, and tests `TestOwnerDefault`, `TestOwnerRoot`, `TestOwnerOverride`.

## Control Flow
Defines `ownerFs`, `_RANDOM_OWNER`, `setupOwnerTest`, and tests `TestOwnerDefault`, `TestOwnerRoot`, `TestOwnerOverride`.

## State And Persistence
The fake fs returns random uid/gid for file attrs; nodefs options either replace ownership with current user, preserve fs owner, or force explicit owner. Risks are platform uid/gid stat differences and root/current-user behavior. Signals validate owner mapping policy.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
The fake fs returns random uid/gid for file attrs; nodefs options either replace ownership with current user, preserve fs owner, or force explicit owner. Risks are platform uid/gid stat differences and root/current-user behavior. Signals validate owner mapping policy.

## Test Signals
The fake fs returns random uid/gid for file attrs; nodefs options either replace ownership with current user, preserve fs owner, or force explicit owner. Risks are platform uid/gid stat differences and root/current-user behavior. Signals validate owner mapping policy.
