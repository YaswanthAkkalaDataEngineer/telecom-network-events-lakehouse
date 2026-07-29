from pathlib import Path
import argparse,shutil
from datetime import datetime
from validate_input_data import validate_all
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'; BACKUPS=ROOT/'data/backups'
FILES=[Path('cdr/cdr.csv'),Path('network_events/network_events.csv'),Path('subscriber_activity/subscriber_activity.csv'),Path('reference/cell_towers.csv'),Path('operations/service_tickets.csv'),Path('operations/outages.csv')]

def main():
    p=argparse.ArgumentParser(); p.add_argument('--source',type=Path,required=True); src=p.parse_args().source.resolve()
    missing=[str(x) for x in FILES if not (src/x).exists()]
    if missing: print('Missing replacement files:', ', '.join(missing)); raise SystemExit(1)
    backup=BACKUPS/datetime.now().strftime('%Y%m%d_%H%M%S'); shutil.copytree(RAW,backup)
    for rel in FILES:
        target=RAW/rel; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src/rel,target)
    errors=validate_all(ROOT)
    if errors:
        shutil.rmtree(RAW); shutil.copytree(backup,RAW); print('Validation failed; old data restored.'); [print('-',e) for e in errors]; raise SystemExit(1)
    print('Replacement successful. Backup:',backup)
if __name__=='__main__': main()
