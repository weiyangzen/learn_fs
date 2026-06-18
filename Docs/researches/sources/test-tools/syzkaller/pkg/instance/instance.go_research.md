## sources/test-tools/syzkaller/pkg/instance/instance.go

Purpose: provides a high-level environment for building syzkaller/kernel artifacts and testing images, patches, bisection candidates, reproducers, and smoke-test manager runs in temporary VM instances.

Important APIs/types/functions: `Env`, `NewEnv`, `BuildSyzkaller`, `BuildKernel`, `CleanKernel`, `SetConfigImage`, `OverrideVMCount`, `TestError`, `CrashError`, `Env.Test`, per-VM `inst.test/testInstance/testRepro/csourceOptions`, `ExecprogCmd`, `RunnerCmd`, `RunSmokeTest`, and `MakeBin`.

Control flow: `NewEnv` validates overcommit-capable VM config and paths. Build methods use optional semaphores, VCS checkout, `make target`, and kernel image build helpers. `Test` completes config, prebuilds C repros, creates reporter and VM pool, runs N VM tests concurrently, first smoke-tests data mmap, then executes syz/C repros and collects coverage. Error transformation distinguishes boot/test/infra/crash cases. Smoke test writes a manager config, runs `syz-manager -mode=smoke-test`, and returns a report from `report.json` or synthetic fatal output.

State and persistence: mutates `mgrconfig.Config` image/object/key/VM JSON fields, writes kernel build output under workdir/image, temporary manager config/report files, and creates VM-side files. `env.optionalFlags` records syzkaller revision capability.

Dependencies and integration: integrates `build`, `vcs`, `vm`, `mgrconfig`, `report`, `csource`, `config`, `targets`, and `tool.OptionalFlags`.

Risks: many host/VM side effects and mutable config fields. Manual command string formatting may mishandle paths with spaces. Old syzkaller compatibility is commit-probe based. Concurrent VM testing shares config and reporter. Smoke-test error classification depends on report file presence.

Test signals: `instance_test.go` checks command-line generation; broader behavior requires integration tests with actual VM pools/builds.
