# Publish Game Monetization & LiveOps Optimizer

Repository: https://github.com/orenzavadi-droid/Game-Monetization-and-LiveOps-Optimizer

## Complete the upload through GitHub

1. Download and extract `Game_Monetization_and_LiveOps_Optimizer_GitHub_Upload.zip`.
2. Open https://github.com/orenzavadi-droid/Game-Monetization-and-LiveOps-Optimizer/upload/main
3. Drag **all files and folders INSIDE** the extracted folder into GitHub, not the parent folder and not the ZIP. GitHub preserves nested folders. Existing README, Dashboard and Learning Kit files are replaced with the complete versions.
4. In the commit message, use `Publish complete LiveOps portfolio project` and click **Commit changes**.
5. Verify that the repository contains `src/`, `sql/`, `tests/`, `data/`, `reports/`, `.github/workflows/ci.yml`, `README.md`, `LEARNING_KIT.html`.

`data/events.csv`, `data/users.csv`, and `data/liveops.sqlite` are deliberately excluded because the project regenerates them.

## Reproduction

```bash
pip install -r requirements.txt
python -m src.run_analysis
python -m pytest -q
```

All data are synthetic; never claim a live A/B test.
