from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'; GOLD=ROOT/'data/processed/gold'

def main():
    cdr=pd.read_csv(RAW/'cdr/cdr.csv').drop_duplicates('cdr_id')
    cdr['call_start_time']=pd.to_datetime(cdr['call_start_time'],errors='coerce'); cdr=cdr.dropna(subset=['call_start_time','subscriber_id','source_tower_id'])
    cdr['event_date']=cdr['call_start_time'].dt.date.astype(str); cdr['is_dropped_call']=(cdr['call_status']=='DROPPED').astype(int); cdr['is_poor_quality']=((cdr['signal_strength_dbm']<-105)|(cdr['latency_ms']>150)).astype(int)
    calls=cdr.groupby(['event_date','region','source_tower_id'],as_index=False).agg(total_calls=('cdr_id','count'),dropped_calls=('is_dropped_call','sum'),avg_latency_ms=('latency_ms','mean'),avg_signal_strength_dbm=('signal_strength_dbm','mean'),poor_quality_calls=('is_poor_quality','sum'),unique_subscribers=('subscriber_id','nunique')).rename(columns={'source_tower_id':'tower_id'})
    calls['drop_rate_pct']=(calls['dropped_calls']/calls['total_calls']*100).round(2)
    ev=pd.read_csv(RAW/'network_events/network_events.csv').drop_duplicates('event_id'); ev['event_time']=pd.to_datetime(ev['event_time'],errors='coerce'); ev['event_date']=ev['event_time'].dt.date.astype(str); ev['is_congested']=((ev['event_type']=='CONGESTION')|(ev['utilization_pct']>90)).astype(int)
    net=ev.groupby(['event_date','region','tower_id'],as_index=False).agg(network_events=('event_id','count'),avg_utilization_pct=('utilization_pct','mean'),avg_availability_pct=('availability_pct','mean'),congestion_events=('is_congested','sum'),avg_packet_loss_pct=('packet_loss_pct','mean'))
    out=calls.merge(net,on=['event_date','region','tower_id'],how='outer').fillna(0); GOLD.mkdir(parents=True,exist_ok=True); out.to_csv(GOLD/'daily_tower_kpis.csv',index=False)
    print(out.head(10).to_string(index=False)); print('Created:',GOLD/'daily_tower_kpis.csv')
if __name__=='__main__': main()
