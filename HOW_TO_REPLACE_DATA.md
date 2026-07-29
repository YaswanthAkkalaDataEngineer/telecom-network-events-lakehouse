# How to Edit or Replace the Data

## Safety first
Use only synthetic data. Never upload real subscriber information, phone numbers, IMSIs, IMEIs, credentials, internal screenshots, production incidents, proprietary schemas, or employer code.

## Edit one CSV on GitHub
1. Open the repository.
2. Open `data/raw` and the required subfolder.
3. Open the CSV.
4. Click the pencil icon.
5. Edit values without changing headers.
6. Commit with a message such as `Update synthetic CDR data`.

## Replace one CSV
1. Copy the matching file from `data/templates`.
2. Edit it in Excel and save as **CSV UTF-8**.
3. Keep the exact original filename.
4. Delete the old GitHub file from its folder.
5. Select **Add file > Upload files**.
6. Upload and commit the replacement.

## Replace all six datasets safely
Prepare this structure:

```text
new_data/
  cdr/cdr.csv
  network_events/network_events.csv
  subscriber_activity/subscriber_activity.csv
  reference/cell_towers.csv
  operations/service_tickets.csv
  operations/outages.csv
```

Run from the project folder:

```powershell
python src/replace_data.py --source "C:\Users\YourName\Downloads\new_data"
```

The script backs up current data, copies the new files, validates headers and duplicate primary keys, and restores the old data if validation fails.

Then run:

```bash
python src/validate_input_data.py
python src/local_pipeline.py
```

Review `data/processed/gold/daily_tower_kpis.csv`, then commit and push.

## Editing rules
- Keep column headers unchanged.
- Use timestamps in `YYYY-MM-DDTHH:MM:SS` format.
- Keep primary keys unique.
- Keep tower IDs consistent across all files.
- Add towers to `cell_towers.csv` before using them in other files.
- Use `Y` or `N` for roaming flags.
- Save as CSV UTF-8.
