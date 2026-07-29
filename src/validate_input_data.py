from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]

def validate_all(root=ROOT):
    contracts=json.loads((root/'config/data_contracts.json').read_text(encoding='utf-8'))
    errors=[]
    for c in contracts.values():
        path=root/c['path']
        if not path.exists(): errors.append(f'Missing file: {path}'); continue
        with path.open('r',newline='',encoding='utf-8-sig') as f:
            r=csv.DictReader(f); headers=r.fieldnames or []; expected=list(c['columns'])
            missing=[x for x in expected if x not in headers]
            if missing: errors.append(f'{path.name}: missing columns {missing}')
            seen=set(); pk=c['primary_key']
            for n,row in enumerate(r,start=2):
                for col,rules in c['columns'].items():
                    if rules.get('required') and not str(row.get(col,'')).strip(): errors.append(f'{path.name} row {n}: missing {col}')
                key=str(row.get(pk,'')).strip()
                if key in seen: errors.append(f'{path.name} row {n}: duplicate {pk} {key}')
                seen.add(key)
    return errors

if __name__=='__main__':
    errors=validate_all()
    if errors:
        print('Validation failed:'); [print('-',e) for e in errors]; raise SystemExit(1)
    print('Validation passed.')
