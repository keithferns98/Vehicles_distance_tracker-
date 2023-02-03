import os
import csv
import pathlib
import datetime
from core.models import TripInfo,VehicleTrails
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help="Load data csvs"
    BASE_DIR = os.path.join(pathlib.Path(__file__).parent.parent.parent.resolve(),"data")
    def read_file(self,base_path=None,file_name=None):
        with open(os.path.join(base_path,file_name),'r') as file:
            data_reader=csv.reader(file)
            next(data_reader)
            for idx,row in enumerate(data_reader):
                yield idx,row
        
    def _load_trip_info(self,file_name):
        for idx,row in self.read_file(self.BASE_DIR,file_name):
            try:
                trip_id,t_name,quantity,vehicle_number,tc_datetime=(row)
                trip_id=int(trip_id)
                quantity=int(quantity)
                dt=datetime.datetime.strptime(tc_datetime,'%Y%m%d%H%M%S')
                if TripInfo.objects.filter(trip_id=trip_id).exists():
                    continue
                TripInfo(trip_id=trip_id,t_name=t_name,quantity=quantity,vehicle_number=vehicle_number,tc_datetime=dt).save()
            except Exception as e:
                print(e)
            
    def _load_vehicle_trails_recs(self):
        path=os.path.join(self.BASE_DIR,'EOL-dump')
        # print(os.listdir(path)[3:])
        boolean={"False":False,"True":True}
        buffer=[]
        MAX_BUFFER_SIZE = 500
        inserted_batched = 0
        for idy,curr_file in enumerate(os.listdir(path)[3:]):
            print(idy,curr_file)
            try:
                for idx,recs in self.read_file(path,curr_file):
                    if len(recs)!=14:
                        print(f"Bad record {idx+1}")
                        continue
                    fk,lic_plate_no,lat,lon,tis,spd,harsh_acceleration,hbk,osf=recs[12],recs[13],recs[5],recs[7],recs[11],recs[10],recs[2],recs[3],recs[8]
                    fk,spd=int(fk),int(float(spd))
                    harsh_acceleration=boolean[harsh_acceleration]
                    hbk=boolean[hbk]
                    osf=boolean[osf]
                    lat,lon=float(lat),float(lon)
                    tis=datetime.datetime.fromtimestamp(int(tis))
                    veh_trails=VehicleTrails(fk_asset=TripInfo.objects.get(trip_id=fk),lic_plate_no=lic_plate_no,lat=lat,lon=lon,tis=tis,spd=spd,harsh_acceleration=harsh_acceleration,hbk=hbk,osf=osf)
                    buffer.append(veh_trails)
                    if len(buffer) > MAX_BUFFER_SIZE:
                        VehicleTrails.objects.bulk_create(buffer)
                        buffer = []
                        inserted_batched += 1
                        print(f"Total batches inserted: {inserted_batched}")
            except Exception as e:
              print(f"Skipping because we can't find ,{e}")   

                
    def handle(self, *args, **options):
        print("Loading TSV data")
        # self._load_trip_info('Trip-Info.csv')
        self._load_vehicle_trails_recs()
    
            