# Pearl Tooling

This directory holds standalone Pearl ecosystem utilities that are useful during
model enablement or validation but are not part of the Silas runtime.

- `model_converter.py` creates experimental Pearl-compatible staging
  checkpoints from raw Hugging Face safetensors models.

Keep user-facing mining commands in `src/silas/cli/` and runtime provider
code in `src/silas/mining/`. Scripts here should be explicit operational
tools that developers run manually.
