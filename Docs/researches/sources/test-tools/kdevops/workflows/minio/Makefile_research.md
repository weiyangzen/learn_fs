## sources/test-tools/kdevops/workflows/minio/Makefile

Purpose: Defines MinIO setup, teardown, benchmark, result-generation, monitoring, and help targets.

Important APIs/types/functions: Targets include `minio`, `minio-install`, `minio-uninstall`, `minio-destroy`, `minio-warp`, `minio-results`, `monitor-results`, and `minio-help`. Uses `MINIO_PLAYBOOK=playbooks/minio.yml`.

Control flow: Setup delegates to install. Install/uninstall/destroy/run invoke `ansible-playbook` with specific tags. Results target checks `workflows/minio/results`, runs `generate_warp_report.py`, prints output locations, and lists recent PNGs.

State and persistence: Ansible creates/destroys MinIO containers/data. Result generation writes HTML/PNG artifacts under `workflows/minio/results`.

Dependencies and integration points: Depends on inventory, `KDEVOPS_EXTRA_VARS`, MinIO playbook tags, Python/matplotlib report generator, and warp result JSON naming.

Risks and test signals: The results target includes Unicode console icons and assumes generated PNG globbing; functional risk is mainly missing Python deps or result files. Test by running `make minio-results` on a directory with sample warp JSON.
