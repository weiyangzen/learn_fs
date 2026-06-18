# sources/test-tools/syzkaller/pkg/subsystem/linux/parents.go

## Purpose

`parents.go` infers and normalizes parent-child relationships among Linux subsystems based on file-path co-occurrence. This allows extraction to prefer specific subsystems while still inheriting broader mailing-list context.

## Important APIs, Types, and Functions

`parentTransformations` coordinates pruning and parent inference. `parentInfo` stores debug comments by parent and child pointer, with `Save` adding explanations. `setParents` infers edges from a `CoincidenceMatrix`. `dropSmallSubsystems`, `dropDuplicateSubsystems`, and `transitiveReduction` clean the generated graph.

## Control Flow

`parentTransformations` first drops subsystems with two or fewer matched files unless they have syscall rules, then drops near-duplicates. `setParents` considers each non-empty matrix pair still present in the input. If at least half of a child's files overlap a larger candidate parent and the child has fewer files, it appends the candidate to `child.Parents`, records debug text, and calls `ReachableParents` to catch loops. `transitiveReduction` removes redundant ancestor links when an intermediate parent already reaches the same ancestor.

## State, Dependencies, Risks, and Test Signals

The code mutates `Subsystem.Parents` and list membership in memory; debug info is returned to callers but not persisted here. Dependencies are the local matrix and `pkg/subsystem`. Risks include integer-threshold roughness (`2*common/childFiles`), pointer-keyed matrices, mutation accumulation if reused lists already have parents, and heuristic duplicate removal based on first list email. Tests cover small drops, duplicate/near-duplicate drops, transitive reduction, and inferred hierarchy from a synthetic filesystem.
