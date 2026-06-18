# sources/test-tools/kdevops/playbooks/roles/vllm/defaults/main.yml

Purpose: default vLLM role values for production-stack source, local paths, results directory, and image selections.

Important APIs/types/functions: defines `vllm_production_stack_repo`, `vllm_production_stack_version`, `vllm_local_path`, `vllm_results_dir`, CPU/GPU-aware `vllm_engine_image_repo/tag`, and router image defaults.

Control flow: no executable flow; defaults drive Docker, Kubernetes, Helm, and bare-metal task files.

State/persistence behavior: path defaults direct state to `/data/vllm` and `/data/vllm-benchmark`.

Dependencies/integration: consumed by vLLM deployment templates and tasks; image defaults assume vLLM CPU image for CPU inference and upstream GPU image otherwise.

Risks/test signals: `latest` tags and image compatibility can drift. Test signals are resolved image names in deployment output and successful pod/container startup.
